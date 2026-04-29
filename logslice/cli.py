"""Command-line interface for logslice."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from typing import Optional

from logslice.pipeline import run
from logslice.sampler import sample_lines


def _parse_dt(value: str) -> datetime:
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise argparse.ArgumentTypeError(f"Cannot parse datetime: {value!r}")


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="logslice",
        description="Extract a time-range slice from a structured log file.",
    )
    p.add_argument("input", help="Path to the log file (use '-' for stdin).")
    p.add_argument("--start", metavar="DATETIME", type=_parse_dt, default=None)
    p.add_argument("--end", metavar="DATETIME", type=_parse_dt, default=None)
    p.add_argument("--output", "-o", metavar="FILE", default=None,
                   help="Write output to FILE instead of stdout.")
    p.add_argument("--format", dest="fmt", choices=("plain", "jsonl", "json"),
                   default="plain")
    p.add_argument("--line-numbers", action="store_true")
    p.add_argument("--stats", action="store_true",
                   help="Print run statistics to stderr after processing.")
    p.add_argument("--stats-format", choices=("text", "json"), default="text")

    # Sampling options (mutually exclusive)
    sample_grp = p.add_mutually_exclusive_group()
    sample_grp.add_argument(
        "--every-nth", metavar="N", type=int, default=None,
        help="Keep only every N-th matched line.",
    )
    sample_grp.add_argument(
        "--sample", metavar="K", type=int, default=None,
        help="Keep a random reservoir sample of at most K matched lines.",
    )
    p.add_argument("--sample-seed", metavar="SEED", type=int, default=None,
                   help="RNG seed for reproducible --sample results.")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    source = sys.stdin if args.input == "-" else open(args.input)
    try:
        matched_lines, stats = run(
            source=source,
            start=args.start,
            end=args.end,
            fmt=args.fmt,
            line_numbers=args.line_numbers,
            output=args.output,
        )

        if args.every_nth is not None or args.sample is not None:
            matched_lines = list(
                sample_lines(
                    matched_lines,
                    every_nth=args.every_nth,
                    reservoir_size=args.sample,
                    seed=args.sample_seed,
                )
            )

        if args.stats:
            from logslice.reporter import report
            report(stats, fmt=args.stats_format, dest=sys.stderr)
    finally:
        if args.input != "-":
            source.close()

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
