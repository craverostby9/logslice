"""Split a log stream into multiple named buckets based on field values or patterns."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, Iterable, Iterator, List, Optional, Tuple


@dataclass
class SplitRule:
    """A single rule mapping a regex pattern to a bucket name."""

    pattern: str
    bucket: str
    _compiled: re.Pattern = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._compiled = re.compile(self.pattern)

    def matches(self, line: str) -> bool:
        return bool(self._compiled.search(line))


@dataclass
class SplitOptions:
    rules: List[SplitRule] = field(default_factory=list)
    default_bucket: str = "default"
    ignore_case: bool = False


def _compile_rules(options: SplitOptions) -> List[SplitRule]:
    flags = re.IGNORECASE if options.ignore_case else 0
    compiled = []
    for rule in options.rules:
        r = SplitRule.__new__(SplitRule)
        r.pattern = rule.pattern
        r.bucket = rule.bucket
        r._compiled = re.compile(rule.pattern, flags)
        compiled.append(r)
    return compiled


def split_lines(
    lines: Iterable[str],
    options: Optional[SplitOptions] = None,
) -> Dict[str, List[str]]:
    """Partition *lines* into buckets according to *options*.

    Returns a dict mapping bucket name -> list of lines.  Order within each
    bucket is preserved.  Lines that match no rule go to ``default_bucket``.
    """
    if options is None:
        options = SplitOptions()

    rules = _compile_rules(options)
    buckets: Dict[str, List[str]] = {}

    for line in lines:
        bucket = options.default_bucket
        for rule in rules:
            if rule.matches(line):
                bucket = rule.bucket
                break
        buckets.setdefault(bucket, []).append(line)

    return buckets


def iter_split(
    lines: Iterable[str],
    options: Optional[SplitOptions] = None,
) -> Iterator[Tuple[str, str]]:
    """Yield *(bucket, line)* pairs without buffering all lines in memory."""
    if options is None:
        options = SplitOptions()

    rules = _compile_rules(options)

    for line in lines:
        bucket = options.default_bucket
        for rule in rules:
            if rule.matches(line):
                bucket = rule.bucket
                break
        yield bucket, line
