"""Composable transform pipeline applied to a stream of log lines."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Iterator, List, Optional

from logslice.contextualizer import contextualise_lines
from logslice.deduplicator import deduplicate_lines
from logslice.filter import compile_filter, filter_lines
from logslice.highlighter import highlight_lines
from logslice.sampler import sample_lines
from logslice.truncator import truncate_lines


@dataclass
class TransformOptions:
    """All optional transformations that can be applied to a line stream."""

    # Filtering
    include_patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    ignore_case: bool = False

    # Deduplication
    dedupe: Optional[str] = None  # None | 'consecutive' | 'global'

    # Sampling
    sample_mode: Optional[str] = None   # None | 'nth' | 'reservoir'
    sample_value: int = 1

    # Truncation
    max_line_length: Optional[int] = None
    truncate_marker: str = "…"

    # Highlighting
    highlight_patterns: List[str] = field(default_factory=list)
    highlight_colour: str = "yellow"

    # Context window
    context_before: int = 0
    context_after: int = 0

    def __init__(self, **kwargs):
        for f_name, f_val in self.__dataclass_fields__.items():  # type: ignore[attr-defined]
            setattr(self, f_name, kwargs.get(f_name, f_val.default_factory() if callable(f_val.default_factory) else f_val.default))  # type: ignore[misc]


def apply_transforms(
    lines: Iterable[str],
    opts: TransformOptions,
) -> Iterator[str]:
    """Apply all enabled transforms in a fixed, sensible order.

    Order: filter → deduplicate → sample → context → truncate → highlight.
    """
    stream: Iterable[str] = lines

    if opts.include_patterns or opts.exclude_patterns:
        compiled = compile_filter(
            opts.include_patterns,
            opts.exclude_patterns,
            ignore_case=opts.ignore_case,
        )
        stream = filter_lines(stream, compiled)

    if opts.dedupe:
        stream = deduplicate_lines(stream, mode=opts.dedupe)

    if opts.sample_mode:
        stream = sample_lines(stream, mode=opts.sample_mode, n=opts.sample_value)

    if opts.context_before > 0 or opts.context_after > 0:
        stream = contextualise_lines(
            stream,
            before=opts.context_before,
            after=opts.context_after,
        )

    if opts.max_line_length is not None:
        stream = truncate_lines(
            stream,
            max_length=opts.max_line_length,
            marker=opts.truncate_marker,
        )

    if opts.highlight_patterns:
        stream = highlight_lines(
            stream,
            patterns=opts.highlight_patterns,
            colour=opts.highlight_colour,
        )

    yield from stream
