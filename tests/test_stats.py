"""Tests for logslice.stats.SliceStats."""

from datetime import datetime

import pytest

from logslice.stats import SliceStats


def _ts(hour: int) -> datetime:
    return datetime(2024, 1, 1, hour, 0, 0)


def test_initial_state():
    s = SliceStats()
    assert s.total_lines_read == 0
    assert s.lines_matched == 0
    assert s.lines_skipped == 0
    assert s.parse_errors == 0
    assert s.first_match_time is None
    assert s.last_match_time is None


def test_match_rate_zero_reads():
    assert SliceStats().match_rate == 0.0


def test_match_rate_calculation():
    s = SliceStats(total_lines_read=10, lines_matched=4)
    assert s.match_rate == pytest.approx(0.4)


def test_record_read_increments():
    s = SliceStats()
    s.record_read()
    s.record_read()
    assert s.total_lines_read == 2


def test_record_skip_increments():
    s = SliceStats()
    s.record_skip()
    assert s.lines_skipped == 1


def test_record_parse_error_increments():
    s = SliceStats()
    s.record_parse_error()
    assert s.parse_errors == 1


def test_record_match_updates_timestamps():
    s = SliceStats()
    s.record_match(_ts(8))
    s.record_match(_ts(9))
    s.record_match(_ts(10))
    assert s.lines_matched == 3
    assert s.first_match_time == _ts(8)
    assert s.last_match_time == _ts(10)


def test_record_match_none_timestamp():
    s = SliceStats()
    s.record_match(None)
    assert s.lines_matched == 1
    assert s.first_match_time is None


def test_to_dict_keys():
    s = SliceStats(total_lines_read=5, lines_matched=3)
    d = s.to_dict()
    assert "total_lines_read" in d
    assert "lines_matched" in d
    assert "match_rate" in d
    assert d["total_lines_read"] == 5


def test_summary_string():
    s = SliceStats(total_lines_read=100, lines_matched=50, lines_skipped=50)
    summary = s.summary()
    assert "100" in summary
    assert "50" in summary
    assert "%" in summary
