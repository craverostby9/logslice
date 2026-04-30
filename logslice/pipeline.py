"""High-level pipeline that wires source → slice → filter → sample → format → write."""

from typing import Iterable, Iterator, Optional

from logslice.filter import filter_lines
from logslice.formatter import format_lines
from logslice.sampler import sample_lines
from logslice.slicer import slice_logs
from logslice.stats import SliceStats, record_match, record_parse_error, record_read, record_skip
from logslice.writer import write_output


def _instrumented_source(
    source: Iterable[str],
    stats: SliceStats,
) -> Iterator[str]:
    """Yield lines from *source* while updating read counters in *stats*."""
    for line in source:
        record_read(stats, line)
        yield line


def run(
    source: Iterable[str],
    *,
    start: Optional[str] = None,
    end: Optional[str] = None,
    include: Optional[str] = None,
    exclude: Optional[str] = None,
    ignore_case: bool = False,
    sample_rate: Optional[int] = None,
    output_format: str = "plain",
    line_numbers: bool = False,
    output: Optional[str] = None,
    stats: Optional[SliceStats] = None,
) -> int:
    """Execute the full logslice pipeline and return the number of lines written.

    Parameters
    ----------
    source:       Iterable of raw log lines (e.g. open file handle).
    start/end:    ISO-8601 timestamp strings for the time slice window.
    include:      Regex pattern — keep only matching lines.
    exclude:      Regex pattern — drop matching lines.
    ignore_case:  Case-insensitive regex matching.
    sample_rate:  Keep every *N*-th line (``None`` = keep all).
    output_format: One of ``plain``, ``jsonl``, ``json``.
    line_numbers: Prefix output lines with their original line number.
    output:       File path for output, or ``None`` for stdout.
    stats:        Optional :class:`SliceStats` instance for instrumentation.
    """
    if stats is None:
        stats = SliceStats()

    pipeline: Iterable[str] = _instrumented_source(source, stats)
    pipeline = slice_logs(pipeline, start=start, end=end)
    pipeline = filter_lines(pipeline, include=include, exclude=exclude, ignore_case=ignore_case)

    if sample_rate is not None:
        pipeline = sample_lines(pipeline, every_nth=sample_rate)

    pipeline = format_lines(pipeline, fmt=output_format, line_numbers=line_numbers)

    return write_output(pipeline, path=output)
