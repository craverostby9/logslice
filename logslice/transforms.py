"""Compose and apply the full transform pipeline to a line iterator."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Iterator, Optional

from logslice.deduplicator import deduplicate_lines
from logslice.filter import compile_filter, filter_lines
from logslice.highlighter import highlight_lines
from logslice.paginator import paginate_lines
from logslice.sampler import sample_lines
from logslice.summarizer import SummaryOptions, summarize_lines
from logslice.truncator import truncate_lines


@dataclass
class TransformOptions:
    # Filtering
    include: list[str] = field(default_factory=list)
    exclude: list[str] = field(default_factory=list)
    ignore_case: bool = False

    # Deduplication
    dedup: Optional[str] = None  # 'consecutive' | 'global'

    # Sampling
    sample_every: Optional[int] = None
    sample_reservoir: Optional[int] = None

    # Truncation
    max_line_length: Optional[int] = None
    truncate_marker: str = "..."

    # Highlighting
    highlight_patterns: list[tuple[str, str]] = field(default_factory=list)

    # Pagination
    offset: int = 0
    limit: Optional[int] = None

    # Summary
    summarize: bool = False
    summary_top_n: int = 10
    summary_group_by: Optional[str] = None
    summary_pattern: Optional[str] = None


def apply_transforms(
    lines: Iterable[str],
    opts: TransformOptions,
) -> tuple[Iterator[str], Optional[object]]:
    """Apply all enabled transforms in order.

    Returns ``(transformed_iterator, summary_or_None)``.
    """
    it: Iterator[str] = iter(lines)

    if opts.include or opts.exclude:
        compiled = compile_filter(opts.include, opts.exclude, opts.ignore_case)
        it = filter_lines(it, compiled)

    if opts.dedup:
        it = deduplicate_lines(it, mode=opts.dedup)

    if opts.sample_every is not None:
        it = sample_lines(it, every_nth=opts.sample_every)
    elif opts.sample_reservoir is not None:
        it = sample_lines(it, reservoir=opts.sample_reservoir)

    if opts.max_line_length is not None:
        it = truncate_lines(it, opts.max_line_length, marker=opts.truncate_marker)

    if opts.highlight_patterns:
        it = highlight_lines(it, opts.highlight_patterns)

    it = paginate_lines(it, offset=opts.offset, limit=opts.limit)

    summary = None
    if opts.summarize:
        s_opts = SummaryOptions(
            top_n=opts.summary_top_n,
            group_by_field=opts.summary_group_by,
            count_pattern=opts.summary_pattern,
        )
        it, summary = summarize_lines(it, s_opts)

    return it, summary
