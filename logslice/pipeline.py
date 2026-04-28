"""High-level pipeline that wires slicer, formatter, writer, and stats together."""

from datetime import datetime
from typing import Iterable, Optional

from logslice.formatter import format_lines
from logslice.parser import parse_timestamp
from logslice.slicer import slice_logs
from logslice.stats import SliceStats
from logslice.writer import write_output


def run(
    source: Iterable[str],
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    fmt: str = "plain",
    output_path: Optional[str] = None,
    line_numbers: bool = False,
    source_path: Optional[str] = None,
) -> SliceStats:
    """Execute the full logslice pipeline and return collected statistics.

    Args:
        source:      Iterable of raw log lines.
        start:       Inclusive start of the time window.
        end:         Inclusive end of the time window.
        fmt:         Output format passed to :func:`format_lines`.
        output_path: File path for output; ``None`` means stdout.
        line_numbers: Whether to include line numbers in formatted output.
        source_path: Label used in stats (e.g. the filename).

    Returns:
        A populated :class:`~logslice.stats.SliceStats` instance.
    """
    stats = SliceStats(source_path=source_path, output_path=output_path)

    def _instrumented_source() -> Iterable[str]:
        for line in source:
            stats.record_read()
            ts = parse_timestamp(line)
            if ts is None and line.strip():
                stats.record_parse_error()
            yield line

    matched_lines = []
    for line in slice_logs(_instrumented_source(), start=start, end=end):
        ts = parse_timestamp(line)
        stats.record_match(ts)
        matched_lines.append(line)

    stats.lines_skipped = stats.total_lines_read - stats.lines_matched

    formatted = list(format_lines(iter(matched_lines), fmt=fmt, line_numbers=line_numbers))
    write_output(iter(formatted), output_path=output_path)

    return stats
