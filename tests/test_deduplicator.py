"""Tests for logslice.deduplicator."""
from __future__ import annotations

import types

import pytest

from logslice.deduplicator import deduplicate_lines


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _run(lines, **kwargs):
    return list(deduplicate_lines(lines, **kwargs))


# ---------------------------------------------------------------------------
# consecutive mode (default)
# ---------------------------------------------------------------------------

def test_no_duplicates_unchanged():
    lines = ["a", "b", "c"]
    assert _run(lines) == lines


def test_consecutive_duplicates_removed():
    lines = ["a", "a", "b", "b", "b", "c"]
    assert _run(lines) == ["a", "b", "c"]


def test_non_consecutive_duplicates_kept_in_consecutive_mode():
    lines = ["a", "b", "a"]
    assert _run(lines) == ["a", "b", "a"]


def test_empty_input_returns_empty():
    assert _run([]) == []


def test_single_line_returned():
    assert _run(["only"]) == ["only"]


def test_strip_before_compare_ignores_whitespace():
    lines = ["hello\n", "hello\n", "world\n"]
    assert _run(lines) == ["hello\n", "world\n"]


def test_no_strip_treats_whitespace_as_significant():
    lines = ["hello", "hello ", "hello"]
    assert _run(lines, strip_before_compare=False) == lines


# ---------------------------------------------------------------------------
# global mode
# ---------------------------------------------------------------------------

def test_global_removes_all_duplicates():
    lines = ["a", "b", "a", "c", "b"]
    assert _run(lines, consecutive_only=False) == ["a", "b", "c"]


def test_global_preserves_first_occurrence_order():
    lines = ["c", "a", "b", "a", "c"]
    assert _run(lines, consecutive_only=False) == ["c", "a", "b"]


def test_global_strip_compare():
    lines = ["foo\n", "bar\n", "foo\n"]
    assert _run(lines, consecutive_only=False) == ["foo\n", "bar\n"]


def test_global_no_strip_keeps_whitespace_variants():
    lines = ["foo", "foo ", "foo"]
    result = _run(lines, consecutive_only=False, strip_before_compare=False)
    assert result == ["foo", "foo "]


# ---------------------------------------------------------------------------
# laziness
# ---------------------------------------------------------------------------

def test_returns_iterator():
    result = deduplicate_lines(iter(["a", "b"]))
    assert isinstance(result, types.GeneratorType)
