"""tail-mode support: follow a growing log file and yield new lines."""

from __future__ import annotations

import io
import time
from pathlib import Path
from typing import Generator, Optional


def tail_lines(
    path: Path,
    *,
    poll_interval: float = 0.25,
    max_wait: Optional[float] = None,
    encoding: str = "utf-8",
    errors: str = "replace",
) -> Generator[str, None, None]:
    """Yield lines appended to *path* in real time.

    The generator opens the file, seeks to the end, then polls for new
    content every *poll_interval* seconds.  If *max_wait* is given the
    generator stops after that many seconds of total elapsed time.

    Parameters
    ----------
    path:
        File to follow.
    poll_interval:
        Seconds between read attempts.
    max_wait:
        Optional hard stop in seconds (useful for tests / CI).
    encoding:
        File encoding forwarded to :func:`open`.
    errors:
        Error handler forwarded to :func:`open`.
    """
    start = time.monotonic()
    with path.open("r", encoding=encoding, errors=errors) as fh:
        fh.seek(0, io.SEEK_END)  # jump to current end
        buf = ""
        while True:
            if max_wait is not None and (time.monotonic() - start) >= max_wait:
                break
            chunk = fh.read()
            if chunk:
                buf += chunk
                while "\n" in buf:
                    line, buf = buf.split("\n", 1)
                    yield line
            else:
                time.sleep(poll_interval)
