"""Tests for logslice.leveler."""

from __future__ import annotations

import pytest

from logslice.leveler import (
    LevelOptions,
    _extract_level,
    _rank,
    filter_by_level,
)


def _run(lines, **kwargs):
    opts = LevelOptions(**kwargs) if kwargs else None
    return list(filter_by_level(lines, opts))


# ---------------------------------------------------------------------------
# _extract_level
# ---------------------------------------------------------------------------

def test_extract_level_info():
    assert _extract_level("2024-01-01 INFO  service started") == "INFO"


def test_extract_level_warn_normalised():
    assert _extract_level("[WARN] disk full") == "WARNING"


def test_extract_level_warning_kept():
    assert _extract_level("WARNING: retrying") == "WARNING"


def test_extract_level_none_when_absent():
    assert _extract_level("plain log line with no level") is None


def test_extract_level_case_insensitive():
    assert _extract_level("debug: connection opened") == "DEBUG"


# ---------------------------------------------------------------------------
# _rank ordering
# ---------------------------------------------------------------------------

def test_rank_ordering():
    assert _rank("TRACE") < _rank("DEBUG") < _rank("INFO") < _rank("ERROR") < _rank("FATAL")


def test_rank_unknown_returns_minus_one():
    assert _rank("UNKNOWN") == -1


# ---------------------------------------------------------------------------
# filter_by_level — no options
# ---------------------------------------------------------------------------

def test_none_opts_returns_all():
    lines = ["INFO hello", "DEBUG world", "ERROR boom"]
    assert list(filter_by_level(lines, None)) == lines


# ---------------------------------------------------------------------------
# min_level
# ---------------------------------------------------------------------------

def test_min_level_excludes_below():
    lines = ["TRACE a", "DEBUG b", "INFO c", "ERROR d"]
    result = _run(lines, min_level="INFO")
    assert result == ["INFO c", "ERROR d"]


def test_min_level_keeps_lines_without_level():
    lines = ["just a plain line", "DEBUG b"]
    result = _run(lines, min_level="ERROR")
    assert "just a plain line" in result


# ---------------------------------------------------------------------------
# max_level
# ---------------------------------------------------------------------------

def test_max_level_excludes_above():
    lines = ["DEBUG a", "INFO b", "ERROR c", "FATAL d"]
    result = _run(lines, max_level="INFO")
    assert result == ["DEBUG a", "INFO b"]


# ---------------------------------------------------------------------------
# min + max range
# ---------------------------------------------------------------------------

def test_range_keeps_within_bounds():
    lines = ["TRACE t", "DEBUG d", "INFO i", "ERROR e", "FATAL f"]
    result = _run(lines, min_level="DEBUG", max_level="ERROR")
    assert result == ["DEBUG d", "INFO i", "ERROR e"]


# ---------------------------------------------------------------------------
# only (allow-list)
# ---------------------------------------------------------------------------

def test_only_keeps_exact_levels():
    lines = ["DEBUG a", "INFO b", "ERROR c"]
    result = _run(lines, only=["INFO", "ERROR"])
    assert result == ["INFO b", "ERROR c"]


def test_only_case_insensitive():
    lines = ["debug msg", "info msg", "error msg"]
    result = _run(lines, only=["info"])
    assert result == ["info msg"]


def test_only_overrides_min_max():
    """When `only` is set, min/max are ignored."""
    lines = ["DEBUG a", "INFO b", "ERROR c"]
    result = _run(lines, only=["DEBUG"], min_level="ERROR")
    assert result == ["DEBUG a"]


def test_empty_input_returns_empty():
    assert _run([], min_level="INFO") == []
