"""Write formatted log slices to a file or stdout."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable


def write_output(
    lines: Iterable[str],
    output_path: str | Path | None = None,
    *,
    encoding: str = "utf-8",
) -> int:
    """Write *lines* to *output_path* (or stdout when *None*).

    Returns the number of lines written.
    """
    count = 0

    if output_path is None:
        for line in lines:
            sys.stdout.write(line if line.endswith("\n") else line + "\n")
            count += 1
        return count

    dest = Path(output_path)
    dest.parent.mkdir(parents=True, exist_ok=True)

    with dest.open("w", encoding=encoding) as fh:
        for line in lines:
            fh.write(line if line.endswith("\n") else line + "\n")
            count += 1

    return count
