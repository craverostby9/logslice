"""Tests for logslice.reporter.report."""

import io
import json
from datetime import datetime

import pytest

from logslice.reporter import report
from logslice.stats import SliceStats


def _populated_stats() -> SliceStats:
    s = SliceStats(
        total_lines_read=200,
        lines_matched=80,
        lines_skipped=120,
        parse_errors=2,
        source_path="app.log",
        output_path="out.log",
    )
    s.first_match_time = datetime(2024, 3, 1, 10, 0, 0)
    s.last_match_time = datetime(2024, 3, 1, 11, 0, 0)
    return s


def test_text_report_contains_key_info():
    buf = io.StringIO()
    report(_populated_stats(), fmt="text", stream=buf)
    output = buf.getvalue()
    assert "200" in output
    assert "80" in output
    assert "app.log" in output
    assert "out.log" in output


def test_text_report_contains_timestamps():
    buf = io.StringIO()
    report(_populated_stats(), fmt="text", stream=buf)
    assert "2024-03-01T10:00:00" in buf.getvalue()


def test_json_report_is_valid_json():
    buf = io.StringIO()
    report(_populated_stats(), fmt="json", stream=buf)
    data = json.loads(buf.getvalue())
    assert data["total_lines_read"] == 200
    assert data["lines_matched"] == 80


def test_json_report_timestamps_iso():
    buf = io.StringIO()
    report(_populated_stats(), fmt="json", stream=buf)
    data = json.loads(buf.getvalue())
    assert data["first_match_time"] == "2024-03-01T10:00:00"


def test_unsupported_format_raises():
    with pytest.raises(ValueError, match="Unsupported"):
        report(SliceStats(), fmt="xml", stream=io.StringIO())


def test_defaults_to_stderr(capsys):
    report(SliceStats(total_lines_read=1, lines_matched=1), fmt="text")
    captured = capsys.readouterr()
    assert "1" in captured.err
