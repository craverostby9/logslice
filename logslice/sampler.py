"""Line sampling utilities for logslice.

Allows reducing output volume by keeping only every N-th matched line
or a random sample of up to a given count.
"""

from __future__ import annotations

import random
from typing import Iterable, Iterator, Optional


def sample_lines(
    lines: Iterable[str],
    every_nth: Optional[int] = None,
    reservoir_size: Optional[int] = None,
    seed: Optional[int] = None,
) -> Iterator[str]:
    """Yield a subset of *lines* according to the chosen sampling strategy.

    Parameters
    ----------
    lines:
        Source iterable of log lines.
    every_nth:
        When set, keep only every N-th line (1-based counter).  Must be >= 1.
    reservoir_size:
        When set, perform reservoir sampling and yield at most this many lines.
        Mutually exclusive with *every_nth*.
    seed:
        Optional RNG seed for reproducible reservoir sampling.

    Raises
    ------
    ValueError
        If both *every_nth* and *reservoir_size* are supplied, or if either
        value is less than 1.
    """
    if every_nth is not None and reservoir_size is not None:
        raise ValueError("Specify at most one of 'every_nth' or 'reservoir_size'.")

    if every_nth is not None:
        if every_nth < 1:
            raise ValueError("'every_nth' must be >= 1.")
        yield from _every_nth(lines, every_nth)
        return

    if reservoir_size is not None:
        if reservoir_size < 1:
            raise ValueError("'reservoir_size' must be >= 1.")
        yield from _reservoir(lines, reservoir_size, seed)
        return

    # No sampling — pass through unchanged.
    yield from lines


def _every_nth(lines: Iterable[str], n: int) -> Iterator[str]:
    for idx, line in enumerate(lines, start=1):
        if idx % n == 0:
            yield line


def _reservoir(lines: Iterable[str], k: int, seed: Optional[int]) -> Iterator[str]:
    rng = random.Random(seed)
    reservoir: list[str] = []
    for idx, line in enumerate(lines):
        if idx < k:
            reservoir.append(line)
        else:
            j = rng.randint(0, idx)
            if j < k:
                reservoir[j] = line
    yield from reservoir
