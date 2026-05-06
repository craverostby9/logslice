"""Composite transform pipeline applied to filtered log lines."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Iterator, List, Optional

from logslice.contextualizer import contextualise_lines
from logslice.deduplicator import deduplicate_lines
from logslice.fieldextractor import extract_fields
from logslice.highlighter import highlight_lines
from logslice.paginator import paginate_lines
from logslice.projector import project_lines
from logslice.sampler import sample_lines
from logslice.truncator import truncate_lines


@dataclass
class TransformOptions:
    # Sampling
    sample_mode: Optional[str] = None      # "nth" | "reservoir"
    sample_n: int = 1
    # Deduplication
    dedup_mode: Optional[str] = None       # "consecutive" | "global"
    # Context lines
    before_context: int = 0
    after_context: int = 0
    # Truncation
    max_line_length: Optional[int] = None
    truncate_marker: str = "..."
    # Highlighting
    highlight_patterns: List[str] = field(default_factory=list)
    highlight_colour: str = "yellow"
    # Field projection
    project_fields: List[str] = field(default_factory=list)
    project_separator: str = "  "
    project_template: Optional[str] = None
    # Pagination
    page_offset: int = 0
    page_limit: Optional[int] = None


def apply_transforms(
    lines: Iterable[str],
    opts: TransformOptions,
) -> Iterator[str]:
    """Apply all enabled transforms to *lines* in a fixed, sensible order."""
    stream: Iterable[str] = lines

    if opts.sample_mode:
        stream = sample_lines(stream, mode=opts.sample_mode, n=opts.sample_n)

    if opts.dedup_mode:
        stream = deduplicate_lines(stream, mode=opts.dedup_mode)

    if opts.before_context or opts.after_context:
        stream = contextualise_lines(
            stream,
            before=opts.before_context,
            after=opts.after_context,
        )

    if opts.max_line_length is not None:
        stream = truncate_lines(
            stream,
            max_length=opts.max_line_length,
            marker=opts.truncate_marker,
        )

    if opts.project_fields:
        stream = project_lines(
            stream,
            opts.project_fields,
            separator=opts.project_separator,
            template=opts.project_template,
        )

    if opts.highlight_patterns:
        stream = highlight_lines(
            stream,
            patterns=opts.highlight_patterns,
            colour=opts.highlight_colour,
        )

    stream = paginate_lines(
        stream,
        offset=opts.page_offset,
        limit=opts.page_limit,
    )

    yield from stream
