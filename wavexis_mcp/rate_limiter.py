"""Per-session rate limiting for WaveXisMCP (M4).

Implements a token bucket algorithm per session.  Each session gets
its own bucket with configurable rate (tokens per second) and burst
(maximum tokens that can accumulate).
"""

from __future__ import annotations

import asyncio
import heapq
import time
from dataclasses import dataclass

_MAX_BUCKETS = 10000
_CLEANUP_INTERVAL_S = 60.0


@dataclass
class _TokenBucket:
    """Token bucket for a single session.

    Attributes:
        rate: Tokens added per second.
        burst: Maximum token capacity.
        tokens: Current token count.
        last_refill: Unix timestamp of last token refill.
    """

    rate: float
    burst: int
    tokens: float
    last_refill: float

    def refill(self, now: float) -> None:
        """Refill tokens based on elapsed time.

        Args:
            now: Current Unix timestamp.
        """
        elapsed = now - self.last_refill
        self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
        self.last_refill = now

    def try_acquire(self, now: float) -> tuple[bool, float]:
        """Attempt to acquire one token.

        Args:
            now: Current Unix timestamp.

        Returns:
            Tuple of ``(acquired, retry_after_ms)``.  If ``acquired`` is
            ``False``, ``retry_after_ms`` indicates how long to wait.
        """
        if self.rate <= 0.0:
            return True, 0.0
        self.refill(now)
        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return True, 0.0
        # Calculate how long until one token is available
        needed = 1.0 - self.tokens
        retry_after_s = needed / self.rate if self.rate > 0 else float("inf")
        retry_after_ms = retry_after_s * 1000
        return False, retry_after_ms


class RateLimiter:
    """Per-session rate limiter using token buckets.

    Each session gets an independent token bucket.  The rate and burst
    are configurable globally via ``configure()``.

    Attributes:
        default_rate: Default tokens per second.
        default_burst: Default maximum burst size.
    """

    def __init__(self, rate: int = 60, burst: int = 10) -> None:
        """Initialize the rate limiter.

        Args:
            rate: Default tokens per second (default: 60).
            burst: Default maximum burst size (default: 10).
        """
        self.default_rate: float = float(max(rate, 1))
        self.default_burst: int = max(burst, 1)
        self._buckets: dict[str, _TokenBucket] = {}
        self._lock = asyncio.Lock()
        self._bucket_ttl: float = 3600.0
        self._max_buckets: int = _MAX_BUCKETS
        self._last_cleanup: float = time.monotonic()

    async def configure(self, rate: int, burst: int) -> None:
        """Update the default rate and burst for new sessions.

        Existing session buckets are updated to the new values.

        Args:
            rate: New tokens per second.
            burst: New maximum burst size.
        """
        async with self._lock:
            self.default_rate = float(max(rate, 1))
            self.default_burst = max(burst, 1)
            for bucket in self._buckets.values():
                bucket.rate = self.default_rate
                bucket.burst = self.default_burst

    def _cleanup_stale_buckets(self, now: float) -> None:
        """Remove buckets that have been inactive longer than ``_bucket_ttl``.

        If the bucket registry exceeds ``_max_buckets``, the least recently
        used buckets are evicted.  Must be called while holding ``self._lock``.

        Args:
            now: Current monotonic timestamp.
        """
        if now - self._last_cleanup >= _CLEANUP_INTERVAL_S:
            self._last_cleanup = now
            stale = [
                sid
                for sid, bucket in self._buckets.items()
                if now - bucket.last_refill > self._bucket_ttl
            ]
            for sid in stale:
                self._buckets.pop(sid, None)

        overflow = len(self._buckets) - self._max_buckets
        if overflow > 0:
            lru = heapq.nsmallest(
                overflow, self._buckets.items(), key=lambda item: item[1].last_refill
            )
            for sid, _ in lru:
                self._buckets.pop(sid, None)

    def _get_or_create_bucket(self, session_id: str, now: float) -> _TokenBucket:
        """Get the bucket for a session, creating one if needed.

        Must be called while holding ``self._lock``.

        Args:
            session_id: Session identifier.
            now: Current monotonic timestamp to use for a new bucket.

        Returns:
            The ``_TokenBucket`` for the session.
        """
        bucket = self._buckets.get(session_id)
        if bucket is None:
            bucket = _TokenBucket(
                rate=self.default_rate,
                burst=self.default_burst,
                tokens=float(self.default_burst),
                last_refill=now,
            )
            self._buckets[session_id] = bucket
        return bucket

    async def acquire(self, session_id: str) -> bool:
        """Attempt to acquire a token for the given session.

        Args:
            session_id: Session identifier.

        Returns:
            ``True`` if the request is allowed, ``False`` if rate limited.
        """
        async with self._lock:
            now = time.monotonic()
            self._cleanup_stale_buckets(now)
            bucket = self._get_or_create_bucket(session_id, now)
            acquired, _ = bucket.try_acquire(now)
            return acquired

    async def check(self, session_id: str) -> tuple[bool, int]:
        """Check rate limit and return status with retry hint.

        Args:
            session_id: Session identifier.

        Returns:
            Tuple of ``(allowed, retry_after_ms)``.  If ``allowed`` is
            ``False``, ``retry_after_ms`` indicates how long to wait.
        """
        async with self._lock:
            now = time.monotonic()
            self._cleanup_stale_buckets(now)
            bucket = self._get_or_create_bucket(session_id, now)
            acquired, retry_after_ms = bucket.try_acquire(now)
            return acquired, int(retry_after_ms)

    async def cleanup(self, session_id: str) -> None:
        """Remove the bucket for a closed session.

        Args:
            session_id: Session identifier to clean up.
        """
        async with self._lock:
            self._buckets.pop(session_id, None)
