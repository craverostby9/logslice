"""Log line grouper — collects consecutive lines that share the same
classifier label into named groups.

This is a thin layer on top of :mod:`logslice.classifier` that bundles
the ``(label, line)`` stream produced by :func:`~logslice.classifier.classify_lines`
into ``(label, [lines])`` chunks.  It is useful for downstream processing
that needs to act on runs of similar log events (e.g. collapsing repeated
error bursts into a single summary entry).
"""

from __future__ import annotations

from itertools import groupby
from typing import Iterable, Iterator, List, Optional, Tuple

from logslice.classifier import ClassifyOptions, classify_lines


def group_by_label(
    lines: Iterable[str],
    options: Optional[ClassifyOptions] = None,
) -> Iterator[Tuple[str, List[str]]]:
    """Yield ``(label, [lines])`` for each consecutive run of same-label lines.

    Parameters
    ----------
    lines:
        Raw log lines to classify and group.
    options:
        Classification rules forwarded to :func:`classify_lines`.  When
        *None* every line receives the ``"other"`` label, so the entire
        input becomes a single group.
    """
    classified = classify_lines(lines, options)
    for label, group in groupby(classified, key=lambda pair: pair[0]):
        yield label, [line for _, line in group]


def flatten_groups(
    groups: Iterable[Tuple[str, List[str]]],
) -> Iterator[str]:
    """Re-expand ``(label, lines)`` groups back to a flat line stream."""
    for _label, lines in groups:
        yield from lines
