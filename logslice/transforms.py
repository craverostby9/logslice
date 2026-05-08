"""Compose all optional transformation steps into a single pipeline pass."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Iterator

from logslice.filter import compile_filter, filter_lines
from logslice.sampler import sample_lines
from logslice.deduplicator import deduplicate_lines
from logslice.truncator import truncate_lines
from logslice.highlighter import highlight_lines
from logslice.paginator import paginate_lines
from logslice.leveler import LevelOptions, filter_by_level
from logslice.anonymizer import AnonymizeOptions, anonymize_lines
from logslice.contextualizer import contextualise_lines
from logslice.projector import project_lines
from logslice.classifier import ClassifyOptions, classify_lines
from logslice.archiver import ArchiveOptions


@dataclass
class TransformOptions:
    # --- filtering ---
    include: list[str] = field(default_factory=list)
    exclude: list[str] = field(default_factory=list)
    ignore_case: bool = False

    # --- level filtering ---
    level: LevelOptions | None = None

    # --- sampling ---
    sample_every: int | None = None
    sample_reservoir: int | None = None

    # --- deduplication ---
    dedup: bool = False
    dedup_global: bool = False

    # --- context ---
    before_context: int = 0
    after_context: int = 0

    # --- truncation ---
    max_line_length: int | None = None
    truncate_marker: str = "..."

    # --- projection ---
    fields: list[str] = field(default_factory=list)
    field_separator: str = "\t"

    # --- classification ---
    classify: ClassifyOptions | None = None

    # --- highlighting ---
    highlight_patterns: list[str] = field(default_factory=list)
    highlight_colour: str = "yellow"

    # --- pagination ---
    offset: int = 0
    limit: int | None = None

    # --- anonymization ---
    anonymize: AnonymizeOptions | None = None

    # --- archiving ---
    archive: ArchiveOptions | None = None


def apply_transforms(
    lines: Iterable[str],
    opts: TransformOptions | None = None,
) -> Iterator[str]:
    """Apply all enabled transforms to *lines* in a fixed, sensible order."""
    if opts is None:
        yield from lines
        return

    stream: Iterable[str] = lines

    # 1. level filter
    if opts.level is not None:
        stream = filter_by_level(stream, opts.level)

    # 2. include / exclude
    if opts.include or opts.exclude:
        f = compile_filter(opts.include, opts.exclude, opts.ignore_case)
        stream = filter_lines(stream, f)

    # 3. anonymize before any output
    if opts.anonymize is not None:
        stream = anonymize_lines(stream, opts.anonymize)

    # 4. context lines
    if opts.before_context or opts.after_context:
        stream = contextualise_lines(
            stream,
            before=opts.before_context,
            after=opts.after_context,
        )

    # 5. deduplication
    if opts.dedup or opts.dedup_global:
        stream = deduplicate_lines(stream, global_dedup=opts.dedup_global)

    # 6. sampling
    if opts.sample_every is not None:
        stream = sample_lines(stream, every_nth=opts.sample_every)
    elif opts.sample_reservoir is not None:
        stream = sample_lines(stream, reservoir=opts.sample_reservoir)

    # 7. truncation
    if opts.max_line_length is not None:
        stream = truncate_lines(
            stream,
            max_length=opts.max_line_length,
            marker=opts.truncate_marker,
        )

    # 8. field projection
    if opts.fields:
        stream = project_lines(
            stream,
            fields=opts.fields,
            separator=opts.field_separator,
        )

    # 9. classification
    if opts.classify is not None:
        stream = classify_lines(stream, opts.classify)

    # 10. highlighting
    if opts.highlight_patterns:
        stream = highlight_lines(
            stream,
            patterns=opts.highlight_patterns,
            colour=opts.highlight_colour,
        )

    # 11. pagination (always last before yield)
    stream = paginate_lines(stream, offset=opts.offset, limit=opts.limit)

    yield from stream
