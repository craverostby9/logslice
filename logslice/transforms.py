"""Composable post-processing transforms applied to the final line stream.

This module wires together :mod:`logslice.highlighter`,
:mod:`logslice.deduplicator`, and any future line-level transforms so that
:mod:`logslice.pipeline` has a single entry-point for optional output
transformations.
"""
from __future__ import annotations

from typing import Iterable, Iterator, List, Optional

from logslice.deduplicator import deduplicate_lines
from logslice.highlighter import highlight_lines, supports_colour


class TransformOptions:
    """Value-object that carries transform configuration."""

    def __init__(
        self,
        *,
        highlight_patterns: Optional[List[str]] = None,
        highlight_colour: str = "yellow",
        ignore_case_highlight: bool = False,
        deduplicate: bool = False,
        deduplicate_global: bool = False,
        colour_output: bool = False,
    ) -> None:
        self.highlight_patterns: List[str] = highlight_patterns or []
        self.highlight_colour = highlight_colour
        self.ignore_case_highlight = ignore_case_highlight
        self.deduplicate = deduplicate
        self.deduplicate_global = deduplicate_global
        self.colour_output = colour_output


def apply_transforms(
    lines: Iterable[str],
    options: TransformOptions,
    output_stream=None,
) -> Iterator[str]:
    """Apply enabled transforms to *lines* in a fixed, sensible order.

    Order:
    1. Deduplication (operates on raw text before colouring).
    2. Highlighting (adds ANSI codes for terminal display).

    Parameters
    ----------
    lines:
        Input line stream.
    options:
        :class:`TransformOptions` instance controlling which transforms run.
    output_stream:
        When provided, used by :func:`~logslice.highlighter.supports_colour`
        to decide whether to apply ANSI codes.
    """
    stream: Iterable[str] = lines

    if options.deduplicate or options.deduplicate_global:
        stream = deduplicate_lines(
            stream,
            consecutive_only=not options.deduplicate_global,
        )

    if options.highlight_patterns:
        use_colour = options.colour_output or (
            output_stream is not None and supports_colour(output_stream)
        )
        if use_colour:
            stream = highlight_lines(
                stream,
                options.highlight_patterns,
                colour=options.highlight_colour,
                ignore_case=options.ignore_case_highlight,
            )

    yield from stream
