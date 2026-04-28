"""Formats and outputs SliceStats reports."""

import json
import sys
from typing import IO, Optional

from logslice.stats import SliceStats

_FORMATS = ("text", "json")


def report(stats: SliceStats, fmt: str = "text", stream: Optional[IO[str]] = None) -> None:
    """Write a stats report to *stream* (defaults to stderr).

    Args:
        stats: Populated :class:`SliceStats` instance.
        fmt:   Output format – ``"text"`` or ``"json"``.
        stream: Destination stream; defaults to ``sys.stderr``.

    Raises:
        ValueError: If *fmt* is not a supported format.
    """
    if fmt not in _FORMATS:
        raise ValueError(f"Unsupported report format {fmt!r}. Choose from {_FORMATS}.")

    if stream is None:
        stream = sys.stderr

    if fmt == "json":
        json.dump(stats.to_dict(), stream, indent=2)
        stream.write("\n")
    else:
        _write_text(stats, stream)


def _write_text(stats: SliceStats, stream: IO[str]) -> None:
    lines = [
        "=== logslice stats ===",
        f"  source      : {stats.source_path or '-'}",
        f"  output      : {stats.output_path or 'stdout'}",
        f"  lines read  : {stats.total_lines_read}",
        f"  matched     : {stats.lines_matched} ({stats.match_rate:.1%})",
        f"  skipped     : {stats.lines_skipped}",
        f"  parse errors: {stats.parse_errors}",
    ]
    if stats.first_match_time:
        lines.append(f"  first match : {stats.first_match_time.isoformat()}")
    if stats.last_match_time:
        lines.append(f"  last match  : {stats.last_match_time.isoformat()}")
    stream.write("\n".join(lines) + "\n")
