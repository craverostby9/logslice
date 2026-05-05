"""Tests for logslice.truncator."""

from __future__ import annotations

import pytest

from logslice.truncator import truncate_line, truncate_lines


# ---------------------------------------------------------------------------
# truncate_line
# ---------------------------------------------------------------------------


def test_short_line_unchanged():
    assert truncate_line("hello", 80) == "hello"


def test_exact_length_unchanged():
    line = "a" * 10
    assert truncate_line(line, 10) == line


def test_long_line_is_truncated():
    line = "a" * 20
    result = truncate_line(line, 10)
    assert len(result) == 10


def test_truncated_line_ends_with_marker():
    line = "a" * 20
    result = truncate_line(line, 10)
    assert result.endswith("...")


def test_custom_marker_used():
    line = "x" * 20
    result = truncate_line(line, 10, marker=">>")
    assert result.endswith(">>")
    assert len(result) == 10


def test_trailing_newline_preserved():
    line = "a" * 20 + "\n"
    result = truncate_line(line, 10)
    assert result.endswith("\n")
    # Body (without newline) should be 10 chars.
    assert len(result.rstrip("\n")) == 10


def test_no_trailing_newline_not_added():
    line = "a" * 20
    result = truncate_line(line, 10)
    assert not result.endswith("\n")


def test_max_length_shorter_than_marker_clips_marker():
    line = "abcdefghij"
    result = truncate_line(line, 2, marker="...")
    assert len(result) == 2


def test_invalid_max_length_raises():
    with pytest.raises(ValueError, match="max_length"):
        truncate_line("hello", 0)


def test_negative_max_length_raises():
    with pytest.raises(ValueError):
        truncate_line("hello", -5)


# ---------------------------------------------------------------------------
# truncate_lines
# ---------------------------------------------------------------------------


def test_truncate_lines_all_short_unchanged():
    lines = ["short\n", "also short\n"]
    result = list(truncate_lines(lines, 80))
    assert result == lines


def test_truncate_lines_mixed():
    lines = ["a" * 5 + "\n", "b" * 20 + "\n"]
    result = list(truncate_lines(lines, 10))
    assert len(result[0].rstrip("\n")) == 5   # untouched
    assert len(result[1].rstrip("\n")) == 10  # truncated


def test_truncate_lines_empty_input():
    assert list(truncate_lines([], 40)) == []


def test_truncate_lines_is_lazy():
    """truncate_lines should return an iterator, not a list."""
    import types
    result = truncate_lines(["hello"], 80)
    assert isinstance(result, types.GeneratorType)
