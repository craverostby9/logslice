"""Line truncation helpers for logslice.

Provides utilities to truncate long log lines to a maximum character width,
optionally appending an ellipsis marker so the reader knows content was cut.
"""

from __future__ import annotations

from typing import Iterable, Iterator

_DEFAULT_MARKER = "..."


def truncate_line(line: str, max_length: int, marker: str = _DEFAULT_MARKER) -> str:
    """Return *line* truncated to *max_length* characters.

    If *line* already fits within *max_length* it is returned unchanged.
    Otherwise the line is cut and *marker* is appended so that the total
    length equals *max_length*.  If *max_length* is shorter than the marker
    itself the marker is itself truncated to *max_length*.

    Args:
        line:       The raw log line (trailing newline is preserved).
        max_length: Maximum number of characters allowed (must be >= 1).
        marker:     Suffix appended to indicate truncation.

    Returns:
        The (possibly truncated) line.

    Raises:
        ValueError: If *max_length* is less than 1.
    """
    if max_length < 1:
        raise ValueError(f"max_length must be >= 1, got {max_length}")

    # Preserve a trailing newline so downstream writers stay consistent.
    trailing_newline = line.endswith("\n")
    body = line.rstrip("\n")

    if len(body) <= max_length:
        return line  # nothing to do

    # Account for the newline when computing available space.
    available = max_length - len(marker)
    if available <= 0:
        truncated = marker[:max_length]
    else:
        truncated = body[:available] + marker

    return truncated + ("\n" if trailing_newline else "")


def truncate_lines(
    lines: Iterable[str],
    max_length: int,
    marker: str = _DEFAULT_MARKER,
) -> Iterator[str]:
    """Yield each line from *lines* truncated to *max_length* characters.

    This is a thin streaming wrapper around :func:`truncate_line` suitable
    for use in the logslice transform pipeline.

    Args:
        lines:      Iterable of raw log lines.
        max_length: Maximum number of characters per line.
        marker:     Suffix used to signal truncation.

    Yields:
        Truncated lines.
    """
    for line in lines:
        yield truncate_line(line, max_length, marker)
