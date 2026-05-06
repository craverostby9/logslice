"""Summarize a stream of log lines into aggregate statistics."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Iterable, Iterator, Optional


@dataclass
class SummaryOptions:
    top_n: int = 10
    group_by_field: Optional[str] = None
    count_pattern: Optional[str] = None


@dataclass
class Summary:
    total_lines: int = 0
    matched_pattern: int = 0
    top_terms: list[tuple[str, int]] = field(default_factory=list)
    group_counts: dict[str, int] = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "total_lines": self.total_lines,
            "matched_pattern": self.matched_pattern,
            "top_terms": [list(t) for t in self.top_terms],
            "group_counts": self.group_counts,
        }


def summarize_lines(
    lines: Iterable[str],
    opts: Optional[SummaryOptions] = None,
) -> tuple[Iterator[str], Summary]:
    """Consume *lines*, build a Summary, and re-yield every line unchanged."""
    if opts is None:
        opts = SummaryOptions()

    pattern_re = re.compile(opts.count_pattern) if opts.count_pattern else None
    term_counter: Counter[str] = Counter()
    group_counter: Counter[str] = Counter()
    summary = Summary()

    collected: list[str] = []
    for line in lines:
        collected.append(line)
        summary.total_lines += 1

        if pattern_re and pattern_re.search(line):
            summary.matched_pattern += 1

        if opts.group_by_field:
            from logslice.fieldextractor import extract_field

            value = extract_field(line, opts.group_by_field)
            if value is not None:
                group_counter[value] += 1

        words = re.findall(r"[\w]{3,}", line.lower())
        term_counter.update(words)

    summary.top_terms = term_counter.most_common(opts.top_n)
    summary.group_counts = dict(group_counter)

    return iter(collected), summary
