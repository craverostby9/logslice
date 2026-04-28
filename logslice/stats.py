"""Statistics collection for log slicing operations."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class SliceStats:
    """Holds statistics gathered during a log slice operation."""

    total_lines_read: int = 0
    lines_matched: int = 0
    lines_skipped: int = 0
    parse_errors: int = 0
    first_match_time: Optional[datetime] = None
    last_match_time: Optional[datetime] = None
    source_path: Optional[str] = None
    output_path: Optional[str] = None

    def record_match(self, ts: Optional[datetime]) -> None:
        """Record a matched line, optionally updating timestamp bounds."""
        self.lines_matched += 1
        if ts is not None:
            if self.first_match_time is None:
                self.first_match_time = ts
            self.last_match_time = ts

    def record_skip(self) -> None:
        self.lines_skipped += 1

    def record_read(self) -> None:
        self.total_lines_read += 1

    def record_parse_error(self) -> None:
        self.parse_errors += 1

    @property
    def match_rate(self) -> float:
        """Fraction of read lines that matched (0.0–1.0)."""
        if self.total_lines_read == 0:
            return 0.0
        return self.lines_matched / self.total_lines_read

    def to_dict(self) -> dict:
        return {
            "total_lines_read": self.total_lines_read,
            "lines_matched": self.lines_matched,
            "lines_skipped": self.lines_skipped,
            "parse_errors": self.parse_errors,
            "match_rate": round(self.match_rate, 4),
            "first_match_time": self.first_match_time.isoformat() if self.first_match_time else None,
            "last_match_time": self.last_match_time.isoformat() if self.last_match_time else None,
            "source_path": self.source_path,
            "output_path": self.output_path,
        }

    def summary(self) -> str:
        """Return a human-readable one-line summary."""
        return (
            f"Read {self.total_lines_read} lines, "
            f"matched {self.lines_matched} "
            f"({self.match_rate:.1%}), "
            f"skipped {self.lines_skipped}, "
            f"parse errors {self.parse_errors}"
        )
