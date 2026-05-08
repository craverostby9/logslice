"""Archive sliced log output to compressed files (gzip / bz2 / plain)."""

from __future__ import annotations

import bz2
import gzip
import io
import os
from dataclasses import dataclass, field
from typing import Iterable, Iterator, Literal

CompressionFormat = Literal["gz", "bz2", "none"]


@dataclass
class ArchiveOptions:
    format: CompressionFormat = "gz"
    compresslevel: int = 6  # 1-9; ignored for 'none'
    suffix_map: dict[str, str] = field(default_factory=lambda: {
        "gz": ".gz",
        "bz2": ".bz2",
        "none": "",
    })

    def output_path(self, base_path: str) -> str:
        """Return *base_path* with the appropriate compression suffix appended."""
        suffix = self.suffix_map.get(self.format, "")
        if base_path.endswith(suffix) or suffix == "":
            return base_path
        return base_path + suffix


def _open_archive(path: str, opts: ArchiveOptions):
    """Return an open writable file-like object for *path* using *opts*."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    if opts.format == "gz":
        return gzip.open(path, "wt", encoding="utf-8", compresslevel=opts.compresslevel)
    if opts.format == "bz2":
        return bz2.open(path, "wt", encoding="utf-8", compresslevel=opts.compresslevel)
    return open(path, "w", encoding="utf-8")


def archive_lines(
    lines: Iterable[str],
    path: str,
    opts: ArchiveOptions | None = None,
) -> tuple[str, int]:
    """Write *lines* to a (possibly compressed) archive file.

    Returns ``(final_path, line_count)`` where *final_path* includes any
    compression suffix automatically appended by :meth:`ArchiveOptions.output_path`.
    """
    if opts is None:
        opts = ArchiveOptions()

    final_path = opts.output_path(path)
    count = 0
    with _open_archive(final_path, opts) as fh:
        for line in lines:
            fh.write(line if line.endswith("\n") else line + "\n")
            count += 1
    return final_path, count


def read_archive(path: str) -> Iterator[str]:
    """Yield lines from a plain, gzip, or bz2 compressed file at *path*."""
    if path.endswith(".gz"):
        opener = gzip.open(path, "rt", encoding="utf-8")
    elif path.endswith(".bz2"):
        opener = bz2.open(path, "rt", encoding="utf-8")
    else:
        opener = open(path, "r", encoding="utf-8")
    with opener as fh:
        yield from fh
