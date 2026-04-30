"""Core log slicing logic — filters log lines within a given time range."""

from datetime import datetime
from typing import Iterator, Optional, TextIO

from logslice.parser import parse_timestamp


def slice_logs(
    source: TextIO,
    start: Optional[datetime],
    end: Optional[datetime],
    inclusive: bool = True,
) -> Iterator[str]:
    """Yield log lines whose timestamps fall within [start, end].

    Lines that cannot be parsed are attached to the previous matched line
    (continuation lines, stack traces, etc.).

    Args:
        source: Readable file-like object containing log lines.
        start: Lower bound datetime (None means no lower bound).
        end: Upper bound datetime (None means no upper bound).
        inclusive: Whether the range boundaries are inclusive.

    Yields:
        Log lines (with newline stripped) within the specified range.

    Raises:
        ValueError: If start is later than end.
    """
    if start is not None and end is not None and start > end:
        raise ValueError(
            f"start ({start!r}) must not be later than end ({end!r})"
        )

    in_range = False
    pending_continuation: list[str] = []

    for raw_line in source:
        line = raw_line.rstrip('\n')
        ts = parse_timestamp(line)

        if ts is None:
            # Continuation line — buffer it; emit only if we're in range
            if in_range:
                yield line
            continue

        # Flush any pending continuation lines now that we have a new timestamp
        # (they were already yielded above if in_range was True)

        in_range = _in_range(ts, start, end, inclusive)
        if in_range:
            yield line


def _in_range(
    ts: datetime,
    start: Optional[datetime],
    end: Optional[datetime],
    inclusive: bool,
) -> bool:
    """Return True if ts falls within the specified range."""
    if inclusive:
        after_start = (start is None) or (ts >= start)
        before_end = (end is None) or (ts <= end)
    else:
        after_start = (start is None) or (ts > start)
        before_end = (end is None) or (ts < end)
    return after_start and before_end
