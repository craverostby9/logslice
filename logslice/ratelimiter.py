"""
logslice.ratelimiter
~~~~~~~~~~~~~~~~~~~~
Rate-limits the output stream by yielding at most *max_lines* lines per
*interval_seconds* window.  Useful when tailing live logs and piping output
to a downstream consumer that cannot keep up.
"""
from __future__ import annotations

import time
from typing import Iterable, Iterator


def rate_limit_lines(
    lines: Iterable[str],
    max_lines: int,
    interval_seconds: float = 1.0,
    *,
    _sleep=time.sleep,
    _now=time.monotonic,
) -> Iterator[str]:
    """Yield lines, blocking when *max_lines* per *interval_seconds* is hit.

    Parameters
    ----------
    lines:
        Source iterable of log lines.
    max_lines:
        Maximum number of lines to emit within each *interval_seconds* window.
        Must be >= 1.
    interval_seconds:
        Duration of each rate-limit window in seconds.  Must be > 0.
    _sleep / _now:
        Injection points for unit-testing without real wall-clock delays.
    """
    if max_lines < 1:
        raise ValueError(f"max_lines must be >= 1, got {max_lines}")
    if interval_seconds <= 0:
        raise ValueError(
            f"interval_seconds must be > 0, got {interval_seconds}"
        )

    window_start = _now()
    emitted = 0

    for line in lines:
        now = _now()
        elapsed = now - window_start

        if elapsed >= interval_seconds:
            # Start a fresh window
            window_start = now
            emitted = 0

        if emitted >= max_lines:
            # We are still inside the current window — wait for it to expire
            remaining = interval_seconds - (_now() - window_start)
            if remaining > 0:
                _sleep(remaining)
            window_start = _now()
            emitted = 0

        yield line
        emitted += 1
