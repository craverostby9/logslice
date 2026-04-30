"""Consecutive and global duplicate-line removal for log streams."""
from __future__ import annotations

from typing import Iterable, Iterator


def deduplicate_lines(
    lines: Iterable[str],
    *,
    consecutive_only: bool = True,
    strip_before_compare: bool = True,
) -> Iterator[str]:
    """Yield lines with duplicates removed.

    Parameters
    ----------
    lines:
        Input line stream.
    consecutive_only:
        When *True* (default) only adjacent duplicate lines are suppressed,
        preserving the original order.  When *False* the first occurrence of
        every unique line is kept and all later occurrences are dropped.
    strip_before_compare:
        When *True* leading/trailing whitespace is ignored during comparison
        but the original line (with whitespace) is yielded.
    """
    if consecutive_only:
        yield from _dedupe_consecutive(lines, strip_before_compare)
    else:
        yield from _dedupe_global(lines, strip_before_compare)


def _key(line: str, strip: bool) -> str:
    return line.strip() if strip else line


def _dedupe_consecutive(
    lines: Iterable[str], strip: bool
) -> Iterator[str]:
    sentinel = object()
    last = sentinel
    for line in lines:
        k = _key(line, strip)
        if k != last:
            yield line
            last = k


def _dedupe_global(
    lines: Iterable[str], strip: bool
) -> Iterator[str]:
    seen: set[str] = set()
    for line in lines:
        k = _key(line, strip)
        if k not in seen:
            seen.add(k)
            yield line
