"""Tests for logslice.tailer."""

from __future__ import annotations

import threading
import time
from pathlib import Path

import pytest

from logslice.tailer import tail_lines


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _write_after(path: Path, lines: list[str], delay: float = 0.05) -> None:
    """Append *lines* to *path* after *delay* seconds (runs in a thread)."""
    def _worker() -> None:
        time.sleep(delay)
        with path.open("a") as fh:
            for line in lines:
                fh.write(line + "\n")
                fh.flush()
                time.sleep(0.02)

    t = threading.Thread(target=_worker, daemon=True)
    t.start()


# ---------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------

def test_tail_yields_new_lines(tmp_path: Path) -> None:
    log = tmp_path / "app.log"
    log.write_text("")  # create empty file

    expected = ["line one", "line two", "line three"]
    _write_after(log, expected, delay=0.05)

    collected = list(
        tail_lines(log, poll_interval=0.02, max_wait=1.0)
    )
    assert collected == expected


def test_tail_ignores_existing_content(tmp_path: Path) -> None:
    log = tmp_path / "app.log"
    log.write_text("old line\n")  # pre-existing content must be skipped

    _write_after(log, ["new line"], delay=0.05)

    collected = list(
        tail_lines(log, poll_interval=0.02, max_wait=0.5)
    )
    assert collected == ["new line"]
    assert "old line" not in collected


def test_tail_stops_after_max_wait(tmp_path: Path) -> None:
    log = tmp_path / "app.log"
    log.write_text("")

    # Nothing is written; generator should stop after max_wait.
    start = time.monotonic()
    collected = list(tail_lines(log, poll_interval=0.05, max_wait=0.2))
    elapsed = time.monotonic() - start

    assert collected == []
    assert elapsed < 1.0, "generator took too long to stop"


def test_tail_handles_partial_lines(tmp_path: Path) -> None:
    """Lines are only yielded once a newline is received."""
    log = tmp_path / "app.log"
    log.write_text("")

    def _write_partial() -> None:
        time.sleep(0.05)
        with log.open("a") as fh:
            fh.write("partial")
            fh.flush()
            time.sleep(0.05)
            fh.write(" complete\n")
            fh.flush()

    t = threading.Thread(target=_write_partial, daemon=True)
    t.start()

    collected = list(tail_lines(log, poll_interval=0.02, max_wait=0.5))
    assert collected == ["partial complete"]
