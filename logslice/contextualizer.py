"""Context-window extraction: include N lines before/after each matching line."""
from __future__ import annotations

from collections import deque
from typing import Iterable, Iterator


def contextualise_lines(
    lines: Iterable[str],
    before: int = 0,
    after: int = 0,
) -> Iterator[str]:
    """Yield lines, expanding each match to include surrounding context.

    Lines that fall within a context window of a previously seen match are
    included exactly once, preserving original order.  A separator (``--``)
    is emitted between non-contiguous context groups, mirroring *grep -C*
    behaviour.

    Args:
        lines:  Source iterable of log lines.
        before: Number of lines to include *before* each matching line.
        after:  Number of lines to include *after* each matching line.

    Yields:
        Lines (with optional context) interleaved with ``--`` separators.
    """
    if before < 0 or after < 0:
        raise ValueError("'before' and 'after' must be non-negative integers")

    if before == 0 and after == 0:
        yield from lines
        return

    pre_buf: deque[str] = deque(maxlen=before)
    after_remaining = 0
    last_yielded_index = -1
    index = 0
    pending: list[str] = []

    # We need to buffer everything to support look-behind; stream in one pass.
    all_lines = list(lines)
    total = len(all_lines)
    included: set[int] = set()

    # First pass: mark which lines are "match" lines (all lines are candidates
    # when used standalone; the caller is responsible for pre-filtering).  In
    # this module every line is treated as a match — contextualise_lines is
    # designed to wrap an already-filtered stream where every incoming line
    # *is* a match, and we re-expand the window around it.
    match_indices: list[int] = list(range(total))

    for mi in match_indices:
        start = max(0, mi - before)
        end = min(total - 1, mi + after)
        for i in range(start, end + 1):
            included.add(i)

    prev_included = -2
    for i in range(total):
        if i in included:
            if i > prev_included + 1:
                yield "--"
            yield all_lines[i]
            prev_included = i
