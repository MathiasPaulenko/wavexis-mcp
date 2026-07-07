"""Unit tests for rate limiter (M4)."""

from __future__ import annotations

import asyncio
import time

import pytest

from wavexis_mcp.rate_limiter import RateLimiter, _TokenBucket


class TestTokenBucket:
    """Tests for the _TokenBucket dataclass."""

    def test_initial_tokens(self) -> None:
        bucket = _TokenBucket(rate=10, burst=5, tokens=5, last_refill=time.monotonic())
        assert bucket.tokens == 5

    def test_refill(self) -> None:
        now = time.monotonic()
        bucket = _TokenBucket(rate=10, burst=5, tokens=0, last_refill=now)
        # Simulate 1 second passing — would add 10 tokens but capped at burst=5
        bucket.refill(now + 1.0)
        assert bucket.tokens == 5  # capped at burst

    def test_refill_cap(self) -> None:
        now = time.monotonic()
        bucket = _TokenBucket(rate=100, burst=5, tokens=3, last_refill=now)
        bucket.refill(now + 10.0)
        assert bucket.tokens == 5  # capped at burst

    def test_try_acquire_success(self) -> None:
        now = time.monotonic()
        bucket = _TokenBucket(rate=10, burst=5, tokens=5, last_refill=now)
        acquired, retry = bucket.try_acquire(now)
        assert acquired is True
        assert retry == 0.0
        assert bucket.tokens == pytest.approx(4.0)

    def test_try_acquire_empty(self) -> None:
        now = time.monotonic()
        bucket = _TokenBucket(rate=10, burst=5, tokens=0, last_refill=now)
        acquired, retry = bucket.try_acquire(now)
        assert acquired is False
        assert retry > 0


class TestRateLimiter:
    """Tests for the RateLimiter class."""

    @pytest.mark.unit
    async def test_acquire_within_burst(self) -> None:
        limiter = RateLimiter(rate=60, burst=10)
        for _ in range(10):
            assert await limiter.acquire("session-1") is True

    @pytest.mark.unit
    async def test_acquire_exceeds_burst(self) -> None:
        limiter = RateLimiter(rate=1, burst=2)
        assert await limiter.acquire("session-1") is True
        assert await limiter.acquire("session-1") is True
        assert await limiter.acquire("session-1") is False

    @pytest.mark.unit
    async def test_per_session_isolation(self) -> None:
        limiter = RateLimiter(rate=1, burst=1)
        assert await limiter.acquire("session-1") is True
        assert await limiter.acquire("session-1") is False
        # Different session has its own bucket
        assert await limiter.acquire("session-2") is True

    @pytest.mark.unit
    async def test_check_returns_retry_after(self) -> None:
        limiter = RateLimiter(rate=10, burst=1)
        allowed, retry = await limiter.check("session-1")
        assert allowed is True
        assert retry == 0

        allowed, retry = await limiter.check("session-1")
        assert allowed is False
        assert retry > 0

    @pytest.mark.unit
    async def test_configure_updates_defaults(self) -> None:
        limiter = RateLimiter(rate=60, burst=10)
        limiter.configure(rate=1, burst=1)
        # New session should use new defaults
        assert await limiter.acquire("new-session") is True
        assert await limiter.acquire("new-session") is False

    @pytest.mark.unit
    async def test_cleanup_removes_bucket(self) -> None:
        limiter = RateLimiter(rate=60, burst=10)
        await limiter.acquire("session-1")
        limiter.cleanup("session-1")
        assert "session-1" not in limiter._buckets

    @pytest.mark.unit
    async def test_refill_over_time(self) -> None:
        limiter = RateLimiter(rate=100, burst=1)
        assert await limiter.acquire("session-1") is True
        assert await limiter.acquire("session-1") is False
        # Wait for refill
        await asyncio.sleep(0.02)  # 20ms = 2 tokens at rate=100
        assert await limiter.acquire("session-1") is True
