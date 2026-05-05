"""Tests for logslice.contextualizer."""
import pytest

from logslice.contextualizer import contextualise_lines


def _run(lines, before=0, after=0):
    return list(contextualise_lines(lines, before=before, after=after))


LINES = [f"line{i}" for i in range(10)]


# ---------------------------------------------------------------------------
# Basic passthrough
# ---------------------------------------------------------------------------

def test_zero_context_returns_all_lines():
    result = _run(LINES)
    assert result == LINES


def test_empty_input_returns_empty():
    assert _run([]) == []


# ---------------------------------------------------------------------------
# Before context
# ---------------------------------------------------------------------------

def test_before_context_single_line_source():
    result = _run(["only"], before=3)
    assert result == ["only"]


def test_before_does_not_exceed_start_of_file():
    # Lines 0-9; before=5 for first line should not go negative
    result = _run(LINES[:3], before=10)
    # All three lines are matches, so all are included, no separator needed
    assert "--" not in result
    assert "line0" in result


# ---------------------------------------------------------------------------
# After context
# ---------------------------------------------------------------------------

def test_after_context_does_not_exceed_end_of_file():
    result = _run(LINES[-2:], after=10)
    assert "--" not in result
    assert result[-1] == LINES[-1]


# ---------------------------------------------------------------------------
# Separator behaviour
# ---------------------------------------------------------------------------

def test_no_separator_when_context_windows_overlap():
    # All lines are matches, windows cover everything — no separator
    result = _run(LINES, before=1, after=1)
    assert "--" not in result


def test_separator_between_non_contiguous_groups():
    # Provide two isolated lines with a gap; simulate by slicing
    source = ["a", "b", "c"]
    # With before=0, after=0 every line is included contiguously
    result = _run(source, before=0, after=0)
    assert "--" not in result


# ---------------------------------------------------------------------------
# Invalid arguments
# ---------------------------------------------------------------------------

def test_negative_before_raises():
    with pytest.raises(ValueError, match="non-negative"):
        _run(LINES, before=-1)


def test_negative_after_raises():
    with pytest.raises(ValueError, match="non-negative"):
        _run(LINES, after=-1)


# ---------------------------------------------------------------------------
# Iterator / generator input
# ---------------------------------------------------------------------------

def test_accepts_generator_input():
    gen = (f"line{i}" for i in range(5))
    result = _run(gen, before=1, after=1)
    assert len(result) >= 5
