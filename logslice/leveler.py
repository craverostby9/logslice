"""Level-based log filtering — keep or reject lines by log severity level."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable, Iterator, List, Optional

# Ordered from least to most severe
_LEVELS = ["TRACE", "DEBUG", "INFO", "NOTICE", "WARNING", "WARN", "ERROR", "CRITICAL", "FATAL"]

# Normalise aliases so comparisons are consistent
_NORMALISE = {"WARN": "WARNING"}

_LEVEL_RANK: dict[str, int] = {
    "TRACE": 0,
    "DEBUG": 1,
    "INFO": 2,
    "NOTICE": 3,
    "WARNING": 4,
    "ERROR": 5,
    "CRITICAL": 6,
    "FATAL": 7,
}

_PATTERN = re.compile(
    r"\b(TRACE|DEBUG|INFO|NOTICE|WARN(?:ING)?|ERROR|CRITICAL|FATAL)\b",
    re.IGNORECASE,
)


@dataclass
class LevelOptions:
    min_level: Optional[str] = None   # inclusive lower bound
    max_level: Optional[str] = None   # inclusive upper bound
    only: List[str] = field(default_factory=list)  # exact allow-list


def _rank(level: str) -> int:
    """Return numeric rank for *level*, normalising aliases first."""
    normalised = _NORMALISE.get(level.upper(), level.upper())
    return _LEVEL_RANK.get(normalised, -1)


def _extract_level(line: str) -> Optional[str]:
    """Return the first log-level token found in *line*, or ``None``."""
    m = _PATTERN.search(line)
    if m is None:
        return None
    raw = m.group(1).upper()
    return _NORMALISE.get(raw, raw)


def _passes(line: str, opts: LevelOptions) -> bool:
    level = _extract_level(line)
    if level is None:
        # Lines without a detectable level are always kept
        return True

    if opts.only:
        allowed = {_NORMALISE.get(o.upper(), o.upper()) for o in opts.only}
        return level in allowed

    rank = _rank(level)
    if opts.min_level is not None and rank < _rank(opts.min_level):
        return False
    if opts.max_level is not None and rank > _rank(opts.max_level):
        return False
    return True


def filter_by_level(
    lines: Iterable[str],
    opts: Optional[LevelOptions] = None,
) -> Iterator[str]:
    """Yield only those *lines* whose severity satisfies *opts*."""
    if opts is None:
        yield from lines
        return

    for line in lines:
        if _passes(line, opts):
            yield line
