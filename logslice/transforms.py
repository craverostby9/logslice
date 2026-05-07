"""Composite transform pipeline applied to a stream of log lines.

This module wires together the individual processing stages (filter,
deduplication, truncation, highlighting, sampling, pagination, projection,
and contextualisation) behind a single :func:`apply_transforms` call so
that the CLI and pipeline layers do not need to know about each stage.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Iterator, List, Optional

from logslice.filter import compile_filter, filter_lines
from logslice.deduplicator import deduplicate_lines
from logslice.truncator import truncate_lines
from logslice.sampler import sample_lines
from logslice.paginator import paginate_lines
from logslice.contextualizer import contextualise_lines
from logslice.highlighter import highlight_lines
from logslice.projector import project_lines


@dataclass
class TransformOptions:
    # filter
    include: List[str] = field(default_factory=list)
    exclude: List[str] = field(default_factory=list)
    ignore_case: bool = False
    # deduplication
    dedup: Optional[str] = None          # None | "consecutive" | "global"
    # truncation
    max_line_length: Optional[int] = None
    truncation_marker: str = "…"
    # sampling
    sample_every: Optional[int] = None
    sample_reservoir: Optional[int] = None
    # pagination
    offset: int = 0
    limit: Optional[int] = None
    # context
    before_context: int = 0
    after_context: int = 0
    # highlight
    highlight_patterns: List[str] = field(default_factory=list)
    highlight_colour: str = "yellow"
    # projection
    fields: List[str] = field(default_factory=list)
    field_separator: str = "\t"
    field_placeholder: str = "-"


def apply_transforms(
    lines: Iterable[str],
    opts: TransformOptions,
) -> Iterator[str]:
    """Apply all enabled transforms in a sensible order and yield results."""
    stream: Iterable[str] = lines

    # 1. filter
    if opts.include or opts.exclude:
        compiled = compile_filter(
            include=opts.include,
            exclude=opts.exclude,
            ignore_case=opts.ignore_case,
        )
        stream = filter_lines(stream, compiled)

    # 2. contextualisation (must run before dedup / truncation)
    if opts.before_context or opts.after_context:
        stream = contextualise_lines(
            stream,
            before=opts.before_context,
            after=opts.after_context,
        )

    # 3. deduplication
    if opts.dedup:
        stream = deduplicate_lines(stream, mode=opts.dedup)

    # 4. sampling
    if opts.sample_every is not None or opts.sample_reservoir is not None:
        stream = sample_lines(
            stream,
            every_nth=opts.sample_every,
            reservoir=opts.sample_reservoir,
        )

    # 5. projection
    if opts.fields:
        stream = project_lines(
            stream,
            fields=opts.fields,
            separator=opts.field_separator,
            placeholder=opts.field_placeholder,
        )

    # 6. truncation
    if opts.max_line_length is not None:
        stream = truncate_lines(
            stream,
            max_length=opts.max_line_length,
            marker=opts.truncation_marker,
        )

    # 7. highlighting
    if opts.highlight_patterns:
        stream = highlight_lines(
            stream,
            patterns=opts.highlight_patterns,
            colour=opts.highlight_colour,
        )

    # 8. pagination (offset + limit applied last)
    stream = paginate_lines(stream, offset=opts.offset, limit=opts.limit)

    yield from stream
