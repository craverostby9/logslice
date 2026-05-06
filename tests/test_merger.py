"""Tests for logslice.merger."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List

import pytest

from logslice.merger import merge_logs


def _ts(hour: int, minute: int = 0, second: int = 0) -> str:
    """Return an ISO-8601 timestamp string for a fixed date."""
    return datetime(2024, 1, 1, hour, minute, second, tzinfo=timezone.utc).isoformat()


def _line(hour: int, msg: str, minute: int = 0, second: int = 0) -> str:
    return f"{_ts(hour, minute, second)} {msg}"


# ---------------------------------------------------------------------------
# Basic merging
# ---------------------------------------------------------------------------

def test_empty_sources_yields_nothing():
    assert list(merge_logs([])) == []


def test_single_source_passthrough():
    lines = [_line(1, "a"), _line(2, "b"), _line(3, "c")]
    assert list(merge_logs([lines])) == lines


def test_two_interleaved_sources():
    src_a = [_line(1, "a"), _line(3, "c")]
    src_b = [_line(2, "b"), _line(4, "d")]
    result = list(merge_logs([src_a, src_b]))
    assert result == [_line(1, "a"), _line(2, "b"), _line(3, "c"), _line(4, "d")]


def test_three_sources_merged_in_order():
    src_a = [_line(1, "a"), _line(6, "f")]
    src_b = [_line(2, "b"), _line(4, "d")]
    src_c = [_line(3, "c"), _line(5, "e")]
    result = list(merge_logs([src_a, src_b, src_c]))
    messages = [r.split(" ", 1)[1] for r in result]
    assert messages == ["a", "b", "c", "d", "e", "f"]


# ---------------------------------------------------------------------------
# Tie-breaking / stability
# ---------------------------------------------------------------------------

def test_stable_mode_preserves_source_order_on_tie():
    ts = _ts(10)
    src_a = [f"{ts} from-A"]
    src_b = [f"{ts} from-B"]
    result = list(merge_logs([src_a, src_b], stable=True))
    assert result[0].endswith("from-A")
    assert result[1].endswith("from-B")


# ---------------------------------------------------------------------------
# Unparseable timestamps
# ---------------------------------------------------------------------------

def test_unparseable_lines_appear_last():
    src_a = [_line(1, "first"), "NO-TIMESTAMP garbage"]
    src_b = [_line(2, "second")]
    result = list(merge_logs([src_a, src_b]))
    assert result[-1] == "NO-TIMESTAMP garbage"
    assert result[0] == _line(1, "first")


def test_all_unparseable_lines_preserved():
    src_a = ["bad line 1", "bad line 2"]
    src_b = ["bad line 3"]
    result = list(merge_logs([src_a, src_b]))
    assert len(result) == 3
    assert set(result) == {"bad line 1", "bad line 2", "bad line 3"}


# ---------------------------------------------------------------------------
# Non-stable (heap) mode
# ---------------------------------------------------------------------------

def test_unstable_mode_still_produces_correct_order():
    src_a = [_line(1, "a"), _line(3, "c")]
    src_b = [_line(2, "b"), _line(4, "d")]
    result = list(merge_logs([src_a, src_b], stable=False))
    timestamps = [r.split(" ", 1)[0] for r in result]
    assert timestamps == sorted(timestamps)
