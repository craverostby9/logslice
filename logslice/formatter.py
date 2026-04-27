"""Output formatting utilities for logslice."""

from __future__ import annotations

import json
from typing import Iterable


SUPPORTED_FORMATS = ("plain", "json", "jsonl")


def format_lines(
    lines: Iterable[str],
    fmt: str = "plain",
    *,
    include_line_numbers: bool = False,
) -> Iterable[str]:
    """Yield formatted output lines.

    Parameters
    ----------
    lines:
        Raw log lines to format.
    fmt:
        One of ``'plain'``, ``'json'``, or ``'jsonl'``.
    include_line_numbers:
        When *True* prefix each line with its 1-based index.
    """
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported format {fmt!r}. Choose from: {', '.join(SUPPORTED_FORMATS)}"
        )

    collected = list(lines)

    if fmt == "plain":
        for idx, line in enumerate(collected, start=1):
            if include_line_numbers:
                yield f"{idx}: {line}"
            else:
                yield line

    elif fmt == "jsonl":
        for idx, line in enumerate(collected, start=1):
            record: dict = {"line": line.rstrip("\n")}
            if include_line_numbers:
                record = {"n": idx, **record}
            yield json.dumps(record)

    elif fmt == "json":
        records = []
        for idx, line in enumerate(collected, start=1):
            record = {"line": line.rstrip("\n")}
            if include_line_numbers:
                record = {"n": idx, **record}
            records.append(record)
        yield json.dumps(records, indent=2)
