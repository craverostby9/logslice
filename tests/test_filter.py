"""Tests for logslice.filter."""

import pytest

from logslice.filter import compile_filter, filter_lines


LINES = [
    "2024-01-01 00:00:01 INFO  service started",
    "2024-01-01 00:00:02 DEBUG checking config",
    "2024-01-01 00:00:03 ERROR connection refused",
    "2024-01-01 00:00:04 INFO  request received",
    "2024-01-01 00:00:05 WARN  slow query detected",
]


def test_no_filters_returns_all():
    result = list(filter_lines(LINES))
    assert result == LINES


def test_include_keeps_matching_lines():
    result = list(filter_lines(LINES, include=r"ERROR|WARN"))
    assert len(result) == 2
    assert all("ERROR" in l or "WARN" in l for l in result)


def test_exclude_drops_matching_lines():
    result = list(filter_lines(LINES, exclude=r"DEBUG"))
    assert all("DEBUG" not in l for l in result)
    assert len(result) == 4


def test_include_and_exclude_combined():
    result = list(filter_lines(LINES, include=r"INFO", exclude=r"request"))
    assert len(result) == 1
    assert "started" in result[0]


def test_ignore_case_include():
    result = list(filter_lines(LINES, include=r"error", ignore_case=True))
    assert len(result) == 1
    assert "ERROR" in result[0]


def test_ignore_case_exclude():
    result = list(filter_lines(LINES, exclude=r"info", ignore_case=True))
    assert all("INFO" not in l for l in result)


def test_empty_source_returns_empty():
    assert list(filter_lines([], include=r"ERROR")) == []


def test_include_no_match_returns_empty():
    result = list(filter_lines(LINES, include=r"CRITICAL"))
    assert result == []


# --- compile_filter ---

def test_compile_filter_keep_all():
    keep = compile_filter()
    assert all(keep(l) for l in LINES)


def test_compile_filter_include():
    keep = compile_filter(include=r"ERROR")
    assert keep("2024-01-01 ERROR something")
    assert not keep("2024-01-01 INFO something")


def test_compile_filter_exclude():
    keep = compile_filter(exclude=r"DEBUG")
    assert not keep("2024-01-01 DEBUG verbose")
    assert keep("2024-01-01 INFO normal")


def test_compile_filter_invalid_regex_raises():
    import re
    with pytest.raises(re.error):
        compile_filter(include=r"[unclosed")
