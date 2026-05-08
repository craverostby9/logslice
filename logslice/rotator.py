"""Log-rotation helper: split a stream into size- or line-count-bounded archive files."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Iterable, Iterator

from logslice.archiver import ArchiveOptions, archive_lines


@dataclass
class RotateOptions:
    max_lines: int | None = None   # rotate after this many lines
    max_bytes: int | None = None   # rotate after approx this many bytes
    archive: ArchiveOptions = field(default_factory=ArchiveOptions)
    name_template: str = "{base}.{index}{ext}"  # {base}, {index}, {ext} placeholders


def _split_name(path: str, opts: ArchiveOptions) -> tuple[str, str]:
    """Return *(base, ext)* where *ext* includes the compression suffix."""
    ext = opts.suffix_map.get(opts.format, "")
    return path, ext


def _chunk(
    lines: Iterable[str],
    max_lines: int | None,
    max_bytes: int | None,
) -> Iterator[list[str]]:
    """Yield successive chunks of *lines* respecting size/count limits."""
    chunk: list[str] = []
    byte_count = 0

    for line in lines:
        chunk.append(line)
        byte_count += len(line.encode())

        line_limit_hit = max_lines is not None and len(chunk) >= max_lines
        byte_limit_hit = max_bytes is not None and byte_count >= max_bytes

        if line_limit_hit or byte_limit_hit:
            yield chunk
            chunk = []
            byte_count = 0

    if chunk:
        yield chunk


def rotate_logs(
    lines: Iterable[str],
    base_path: str,
    opts: RotateOptions | None = None,
) -> list[tuple[str, int]]:
    """Write *lines* to one or more archive files, rotating as needed.

    Returns a list of ``(final_path, line_count)`` tuples, one per file written.
    """
    if opts is None:
        opts = RotateOptions()

    base, ext = _split_name(base_path, opts.archive)
    results: list[tuple[str, int]] = []

    for index, chunk in enumerate(_chunk(lines, opts.max_lines, opts.max_bytes)):
        segment_path = opts.name_template.format(
            base=base, index=index, ext=ext
        )
        final, count = archive_lines(chunk, segment_path, opts.archive)
        results.append((final, count))

    return results
