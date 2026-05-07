"""Compose and apply a chain of line-level transforms.

This module acts as the central wiring point that builds a single generator
pipeline from individual transform options so that the pipeline module only
needs to call :func:`apply_transforms`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Iterator, List, Optional

from logslice.anonymizer import AnonymizeOptions, anonymize_lines
from logslice.classifier import ClassifyOptions, classify_lines
from logslice.contextualizer import contextualise_lines
from logslice.deduplicator import deduplicate_lines
from logslice.filter import compile_filter, filter_lines
from logslice.highlighter import highlight_lines
from logslice.leveler import LevelOptions, filter_by_level
from logslice.paginator import paginate_lines
from logslice.projector import project_lines
from logslice.sampler import sample_lines
from logslice.splitter import SplitOptions, iter_split
from logslice.truncator import truncate_lines


@dataclass
class TransformOptions:
    # filtering
    include: Optional[List[str]] = None
    exclude: Optional[List[str]] = None
    ignore_case: bool = False
    level: Optional[LevelOptions] = None
    # deduplication
    dedup: Optional[str] = None  # "consecutive" | "global"
    # sampling
    sample_n: Optional[int] = None
    sample_mode: str = "nth"
    sample_seed: Optional[int] = None
    # context
    before: int = 0
    after: int = 0
    # truncation
    max_width: Optional[int] = None
    truncate_marker: str = "..."
    # pagination
    offset: int = 0
    limit: Optional[int] = None
    # projection
    fields: Optional[List[str]] = None
    field_sep: str = "\t"
    # anonymisation
    anonymize: Optional[AnonymizeOptions] = None
    # classification
    classify: Optional[ClassifyOptions] = None
    # splitting (bucket filter — only lines in *keep_buckets* pass through)
    split: Optional[SplitOptions] = None
    keep_buckets: Optional[List[str]] = None
    # highlighting
    highlight: Optional[List[str]] = None
    highlight_colour: str = "yellow"


def apply_transforms(
    lines: Iterable[str],
    options: Optional[TransformOptions] = None,
) -> Iterator[str]:
    """Apply all enabled transforms in a fixed, sensible order."""
    if options is None:
        options = TransformOptions()

    stream: Iterable[str] = lines

    # 1. level filtering
    if options.level is not None:
        stream = filter_by_level(stream, options.level)

    # 2. keyword filtering
    if options.include or options.exclude:
        f = compile_filter(
            include=options.include or [],
            exclude=options.exclude or [],
            ignore_case=options.ignore_case,
        )
        stream = filter_lines(stream, f)

    # 3. anonymisation
    if options.anonymize is not None:
        stream = anonymize_lines(stream, options.anonymize)

    # 4. deduplication
    if options.dedup:
        stream = deduplicate_lines(stream, mode=options.dedup)

    # 5. context lines
    if options.before or options.after:
        stream = contextualise_lines(
            stream, before=options.before, after=options.after
        )

    # 6. sampling
    if options.sample_n is not None:
        stream = sample_lines(
            stream,
            n=options.sample_n,
            mode=options.sample_mode,
            seed=options.sample_seed,
        )

    # 7. splitting / bucket filtering
    if options.split is not None and options.keep_buckets is not None:
        keep = set(options.keep_buckets)
        stream = (
            line for bucket, line in iter_split(stream, options.split)
            if bucket in keep
        )

    # 8. classification (attaches label prefix — optional downstream use)
    if options.classify is not None:
        stream = classify_lines(stream, options.classify)

    # 9. projection
    if options.fields:
        stream = project_lines(
            stream, fields=options.fields, separator=options.field_sep
        )

    # 10. truncation
    if options.max_width is not None:
        stream = truncate_lines(
            stream,
            max_width=options.max_width,
            marker=options.truncate_marker,
        )

    # 11. highlighting
    if options.highlight:
        stream = highlight_lines(
            stream,
            patterns=options.highlight,
            colour=options.highlight_colour,
        )

    # 12. pagination (always last so counts are post-filter)
    stream = paginate_lines(stream, offset=options.offset, limit=options.limit)

    yield from stream
