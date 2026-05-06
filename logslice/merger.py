"""Merge multiple sorted log streams into a single chronologically ordered stream."""

from __future__ import annotations

import heapq
from typing import Iterable, Iterator, List, Optional, Tuple

from logslice.parser import parse_timestamp


def _timestamped(lines: Iterable[str], source_index: int) -> Iterator[Tuple]:
    """Yield (timestamp_or_None, source_index, line) tuples for heapq merging."""
    for line in lines:
        ts = parse_timestamp(line)
        yield (ts, source_index, line)


def _sort_key(entry: Tuple) -> Tuple:
    """Return a sort key that places None timestamps last."""
    ts, idx, _line = entry
    # datetime objects are comparable; None sorts last via (1, idx) vs (0, ts)
    if ts is None:
        return (1, idx, 0)
    return (0, ts, idx)


def merge_logs(
    sources: List[Iterable[str]],
    stable: bool = True,
) -> Iterator[str]:
    """Merge multiple log line iterables into one time-ordered stream.

    Parameters
    ----------
    sources:
        An ordered list of iterables, each yielding log lines.  Each source
        is assumed to be internally sorted (as produced by ``slice_logs``).
    stable:
        When *True* (default) lines with identical timestamps preserve their
        original source order.  When *False* a lighter heap-merge is used that
        may interleave ties arbitrarily.

    Yields
    ------
    str
        Merged log lines in ascending timestamp order.  Lines whose timestamp
        cannot be parsed are appended after all timestamped lines.
    """
    if not sources:
        return

    if stable:
        # Collect all entries and sort with a stable key
        all_entries = []
        for idx, source in enumerate(sources):
            for line in source:
                ts = parse_timestamp(line)
                all_entries.append((ts, idx, line))
        all_entries.sort(key=_sort_key)
        for _ts, _idx, line in all_entries:
            yield line
    else:
        # Heap-based streaming merge — efficient when sources are pre-sorted
        iterators = [
            _timestamped(src, idx) for idx, src in enumerate(sources)
        ]
        for _ts, _idx, line in heapq.merge(*iterators, key=_sort_key):
            yield line
