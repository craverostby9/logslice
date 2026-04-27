"""Unit tests for logslice.slicer."""

import io
from datetime import datetime

import pytest

from logslice.slicer import slice_logs, _in_range

SAMPLE_LOG = """2024-01-15 10:00:00 INFO  Service started
2024-01-15 10:01:00 DEBUG Processing request 1
    at com.example.Handler.handle(Handler.java:55)
2024-01-15 10:05:00 WARN  High latency detected
2024-01-15 10:10:00 ERROR Request failed
2024-01-15 10:15:00 INFO  Recovered
"""


def _make_source(text: str) -> io.StringIO:
    return io.StringIO(text)


def test_slice_full_range():
    src = _make_source(SAMPLE_LOG)
    lines = list(slice_logs(src, None, None))
    assert len(lines) == 6  # 5 timestamped + 1 continuation


def test_slice_start_only():
    src = _make_source(SAMPLE_LOG)
    start = datetime(2024, 1, 15, 10, 5, 0)
    lines = list(slice_logs(src, start, None))
    assert all("10:05" in l or "10:10" in l or "10:15" in l for l in lines)
    assert len(lines) == 3


def test_slice_end_only():
    src = _make_source(SAMPLE_LOG)
    end = datetime(2024, 1, 15, 10, 1, 0)
    lines = list(slice_logs(src, None, end))
    # 10:00 line + 10:01 line + continuation
    assert len(lines) == 3


def test_slice_start_and_end():
    src = _make_source(SAMPLE_LOG)
    start = datetime(2024, 1, 15, 10, 1, 0)
    end = datetime(2024, 1, 15, 10, 5, 0)
    lines = list(slice_logs(src, start, end))
    assert len(lines) == 3  # 10:01 + continuation + 10:05


def test_slice_exclusive_boundaries():
    src = _make_source(SAMPLE_LOG)
    start = datetime(2024, 1, 15, 10, 1, 0)
    end = datetime(2024, 1, 15, 10, 10, 0)
    lines = list(slice_logs(src, start, end, inclusive=False))
    assert not any("10:01" in l for l in lines)
    assert not any("10:10" in l for l in lines)
    assert any("10:05" in l for l in lines)


def test_in_range_no_bounds():
    ts = datetime(2024, 1, 1, 12, 0, 0)
    assert _in_range(ts, None, None, True) is True


def test_in_range_out_of_bounds():
    ts = datetime(2024, 1, 1, 12, 0, 0)
    start = datetime(2024, 1, 1, 13, 0, 0)
    assert _in_range(ts, start, None, True) is False
