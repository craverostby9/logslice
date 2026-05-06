"""Line projector: reformat log lines to show only selected fields."""

from __future__ import annotations

from typing import Iterable, Iterator, List, Optional

from logslice.fieldextractor import extract_field

_DEFAULT_SEP = "  "


def _format_row(
    line: str,
    fields: List[str],
    separator: str,
    missing: str,
    template: Optional[str],
) -> str:
    """Render a single log line using the requested fields."""
    values = {
        field: (extract_field(line, field) or missing)
        for field in fields
    }
    if template:
        try:
            return template.format(**values)
        except KeyError:
            pass
    return separator.join(values[f] for f in fields)


def project_lines(
    lines: Iterable[str],
    fields: Iterable[str],
    *,
    separator: str = _DEFAULT_SEP,
    missing: str = "-",
    template: Optional[str] = None,
) -> Iterator[str]:
    """Yield reformatted versions of *lines* containing only *fields*.

    Parameters
    ----------
    lines:
        Source log lines.
    fields:
        Ordered list of field names to include in the output.
    separator:
        String placed between field values when no *template* is given.
    missing:
        Placeholder used when a field is absent from a line.
    template:
        Optional Python format string, e.g. ``"{level} {msg}"``.  When
        supplied, *separator* is ignored.
    """
    field_list = list(fields)
    if not field_list:
        yield from lines
        return

    for line in lines:
        yield _format_row(line, field_list, separator, missing, template)
