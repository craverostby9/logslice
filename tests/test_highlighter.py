"""Tests for logslice.highlighter."""
from __future__ import annotations

import io
import re

import pytest

from logslice.highlighter import (
    _colourise,
    _COLOURS,
    _RESET,
    highlight_lines,
    supports_colour,
)


# ---------------------------------------------------------------------------
# _colourise
# ---------------------------------------------------------------------------

def test_colourise_wraps_with_ansi():
    result = _colourise("hello", "red")
    assert result.startswith(_COLOURS["red"])
    assert result.endswith(_RESET)
    assert "hello" in result


def test_colourise_unknown_colour_passthrough():
    assert _colourise("hello", "ultraviolet") == "hello"


# ---------------------------------------------------------------------------
# highlight_lines
# ---------------------------------------------------------------------------

def _strip_ansi(text: str) -> str:
    return re.sub(r"\033\[[0-9;]*m", "", text)


def test_no_patterns_yields_unchanged():
    lines = ["foo bar", "baz qux"]
    assert list(highlight_lines(lines, [])) == lines


def test_matching_pattern_adds_ansi():
    lines = ["hello world"]
    result = list(highlight_lines(lines, ["world"], colour="cyan"))
    assert _COLOURS["cyan"] in result[0]
    assert _strip_ansi(result[0]) == "hello world"


def test_non_matching_line_unchanged():
    lines = ["nothing here"]
    result = list(highlight_lines(lines, ["xyz"]))
    assert result == lines


def test_multiple_patterns_all_highlighted():
    lines = ["foo and bar"]
    result = list(highlight_lines(lines, ["foo", "bar"], colour="red"))
    plain = _strip_ansi(result[0])
    assert plain == "foo and bar"
    assert result[0].count(_COLOURS["red"]) == 2


def test_ignore_case_flag():
    lines = ["ERROR: something failed"]
    result_sensitive = list(highlight_lines(lines, ["error"], colour="red"))
    result_insensitive = list(
        highlight_lines(lines, ["error"], colour="red", ignore_case=True)
    )
    # case-sensitive should NOT match
    assert result_sensitive == lines
    # case-insensitive SHOULD match
    assert _COLOURS["red"] in result_insensitive[0]


def test_generator_is_lazy():
    """highlight_lines must return an iterator, not a list."""
    import types
    result = highlight_lines(iter(["a", "b"]), ["a"])
    assert isinstance(result, types.GeneratorType)


# ---------------------------------------------------------------------------
# supports_colour
# ---------------------------------------------------------------------------

def test_supports_colour_false_for_stringio():
    assert supports_colour(io.StringIO()) is False


def test_supports_colour_false_for_non_tty(tmp_path):
    fh = open(tmp_path / "out.txt", "w")
    try:
        assert supports_colour(fh) is False
    finally:
        fh.close()
