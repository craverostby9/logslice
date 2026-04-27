"""Command-line interface for logslice."""

import sys
from datetime import datetime
from typing import Optional

import click

from logslice.slicer import slice_logs

DATETIME_FORMATS = [
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M",
    "%Y-%m-%d %H:%M",
    "%Y-%m-%d",
]


def _parse_dt(value: Optional[str]) -> Optional[datetime]:
    if value is None:
        return None
    for fmt in DATETIME_FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise click.BadParameter(
        f"Cannot parse '{value}'. Use ISO format, e.g. '2024-01-15 13:45:00'."
    )


@click.command()
@click.argument("logfile", type=click.Path(exists=True, readable=True, allow_dash=True))
@click.option("-s", "--start", default=None, help="Start datetime (inclusive).")
@click.option("-e", "--end", default=None, help="End datetime (inclusive).")
@click.option(
    "--exclusive",
    is_flag=True,
    default=False,
    help="Treat start/end boundaries as exclusive.",
)
@click.option("-o", "--output", default="-", help="Output file (default: stdout).")
def main(logfile: str, start: str, end: str, exclusive: bool, output: str) -> None:
    """Extract a time-range slice from LOGFILE."""
    start_dt = _parse_dt(start)
    end_dt = _parse_dt(end)

    opener = click.open_file(logfile, "r")
    out = click.open_file(output, "w")

    with opener as src, out as dst:
        count = 0
        for line in slice_logs(src, start_dt, end_dt, inclusive=not exclusive):
            dst.write(line + "\n")
            count += 1

    click.echo(f"[logslice] {count} line(s) written.", err=True)


if __name__ == "__main__":
    main()
