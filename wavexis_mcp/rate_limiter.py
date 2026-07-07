"""Per-session rate limiting for WaveXisMCP (M4).

Implements a token bucket algorithm per session.  Each session gets
its own bucket with configurable rate (tokens per second) and burst
(maximum tokens that can accumulate).
"""

from __future__ import annotations

import time
from dataclasses import dataclass


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
        self.default_rate: float = float(rate)
        self.default_burst: int = burst
        self._buckets: dict[str, _TokenBucket] = {}

    def configure(self, rate: int, burst: int) -> None:
        """Update the default rate and burst for new sessions.

        Existing session buckets are updated to the new values.

        Args:
            rate: New tokens per second.
            burst: New maximum burst size.
        """
        self.default_rate = float(rate)
        self.default_burst = burst
        for bucket in self._buckets.values():
            bucket.rate = self.default_rate
            bucket.burst = burst

    def _get_or_create(self, session_id: str) -> _TokenBucket:
        """Get the bucket for a session, creating one if needed.

        Args:
            session_id: Session identifier.

        Returns:
            The ``_TokenBucket`` for the session.
        """
        if session_id not in self._buckets:
            now = time.monotonic()
            self._buckets[session_id] = _TokenBucket(
                rate=self.default_rate,
                burst=self.default_burst,
                tokens=float(self.default_burst),
                last_refill=now,
            )
        return self._buckets[session_id]

    async def acquire(self, session_id: str) -> bool:
        """Attempt to acquire a token for the given session.

        Args:
            session_id: Session identifier.

        Returns:
            ``True`` if the request is allowed, ``False`` if rate limited.
        """
        bucket = self._get_or_create(session_id)
        acquired, _ = bucket.try_acquire(time.monotonic())
        return acquired

    async def check(self, session_id: str) -> tuple[bool, int]:
        """Check rate limit and return status with retry hint.

        Args:
            session_id: Session identifier.

        Returns:
            Tuple of ``(allowed, retry_after_ms)``.  If ``allowed`` is
            ``False``, ``retry_after_ms`` indicates how long to wait.
        """
        bucket = self._get_or_create(session_id)
        acquired, retry_after_ms = bucket.try_acquire(time.monotonic())
        return acquired, int(retry_after_ms)

    def cleanup(self, session_id: str) -> None:
        """Remove the bucket for a closed session.

        Args:
            session_id: Session identifier to clean up.
        """
        self._buckets.pop(session_id, None)
