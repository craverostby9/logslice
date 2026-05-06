"""Pagination helpers — limit and offset for log line output."""
from __future__ import annotations

from typing import Iterable, Iterator


def paginate_lines(
    lines: Iterable[str],
    *,
    offset: int = 0,
    limit: int | None = None,
) -> Iterator[str]:
    """Yield *lines* after skipping *offset* entries, stopping after *limit*.

    Parameters
    ----------
    lines:
        Source iterable of log lines.
    offset:
        Number of lines to skip from the start.  Must be >= 0.
    limit:
        Maximum number of lines to yield.  ``None`` means no upper bound.
        Must be > 0 when supplied.

    Raises
    ------
    ValueError
        If *offset* < 0 or *limit* is not None and < 1.
    """
    if offset < 0:
        raise ValueError(f"offset must be >= 0, got {offset}")
    if limit is not None and limit < 1:
        raise ValueError(f"limit must be >= 1, got {limit}")

    emitted = 0
    for idx, line in enumerate(lines):
        if idx < offset:
            continue
        if limit is not None and emitted >= limit:
            return
        yield line
        emitted += 1
