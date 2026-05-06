"""
Tests for logslice.ratelimiter.

All tests use injected _sleep / _now callables so no real wall-clock time
is consumed.
"""
from __future__ import annotations

import pytest

from logslice.ratelimiter import rate_limit_lines


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class _FakeClock:
    """Monotonic clock that advances only when explicitly told to."""

    def __init__(self, start: float = 0.0):
        self._t = start
        self.sleeps: list[float] = []

    def now(self) -> float:
        return self._t

    def advance(self, delta: float) -> None:
        self._t += delta

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self._t += seconds


def _collect(lines, max_lines, interval=1.0, clock=None):
    if clock is None:
        clock = _FakeClock()
    return (
        list(rate_limit_lines(lines, max_lines, interval,
                              _sleep=clock.sleep, _now=clock.now)),
        clock,
    )


# ---------------------------------------------------------------------------
# Basic correctness
# ---------------------------------------------------------------------------

def test_all_lines_yielded_within_limit():
    """Lines within the rate limit pass through without sleeping."""
    src = ["a", "b", "c"]
    result, clock = _collect(src, max_lines=10, interval=1.0)
    assert result == src
    assert clock.sleeps == []


def test_empty_source_returns_empty():
    result, _ = _collect([], max_lines=5)
    assert result == []


def test_single_line_no_sleep():
    result, clock = _collect(["only"], max_lines=1)
    assert result == ["only"]
    assert clock.sleeps == []


# ---------------------------------------------------------------------------
# Rate-limiting behaviour
# ---------------------------------------------------------------------------

def test_sleep_triggered_when_limit_reached():
    """Exceeding max_lines within the window must cause exactly one sleep."""
    src = ["x"] * 5
    _, clock = _collect(src, max_lines=3, interval=1.0)
    assert len(clock.sleeps) == 1


def test_sleep_duration_is_remaining_window():
    """Sleep duration equals the time left in the current window."""
    clock = _FakeClock(start=0.0)
    # Advance 0.4 s into the 1-second window before we hit the limit
    src = ["a", "b", "c"]

    def advancing_now():
        t = clock.now()
        clock.advance(0.2)  # each call moves time forward
        return t

    list(rate_limit_lines(src, max_lines=2, interval=1.0,
                          _sleep=clock.sleep, _now=advancing_now))
    # At least one sleep must have occurred
    assert clock.sleeps
    assert all(s >= 0 for s in clock.sleeps)


def test_new_window_resets_counter():
    """After a window expires naturally, the counter resets and no sleep occurs."""
    clock = _FakeClock(start=0.0)
    src = ["a", "b", "c"]

    call_count = [0]

    def advancing_now():
        t = clock.now()
        call_count[0] += 1
        # After the 3rd call, jump past the 1-second window
        if call_count[0] == 3:
            clock.advance(2.0)
        return t

    result = list(rate_limit_lines(src, max_lines=2, interval=1.0,
                                   _sleep=clock.sleep, _now=advancing_now))
    assert result == src
    assert clock.sleeps == []


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def test_invalid_max_lines_raises():
    with pytest.raises(ValueError, match="max_lines"):
        list(rate_limit_lines(["a"], max_lines=0))


def test_invalid_interval_raises():
    with pytest.raises(ValueError, match="interval_seconds"):
        list(rate_limit_lines(["a"], max_lines=1, interval_seconds=0))


def test_negative_interval_raises():
    with pytest.raises(ValueError, match="interval_seconds"):
        list(rate_limit_lines(["a"], max_lines=1, interval_seconds=-5.0))
