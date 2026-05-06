"""Tests for logslice.paginator."""
from __future__ import annotations

import pytest

from logslice.paginator import paginate_lines


def _run(lines, **kwargs):
    return list(paginate_lines(lines, **kwargs))


SAMPLE = ["line1", "line2", "line3", "line4", "line5"]


# ---------------------------------------------------------------------------
# Basic behaviour
# ---------------------------------------------------------------------------

def test_no_options_returns_all():
    assert _run(SAMPLE) == SAMPLE


def test_limit_restricts_output():
    assert _run(SAMPLE, limit=3) == ["line1", "line2", "line3"]


def test_offset_skips_leading_lines():
    assert _run(SAMPLE, offset=2) == ["line3", "line4", "line5"]


def test_offset_and_limit_combined():
    assert _run(SAMPLE, offset=1, limit=2) == ["line2", "line3"]


def test_offset_beyond_length_returns_empty():
    assert _run(SAMPLE, offset=10) == []


def test_limit_larger_than_source_returns_all():
    assert _run(SAMPLE, limit=100) == SAMPLE


def test_offset_equals_length_returns_empty():
    assert _run(SAMPLE, offset=len(SAMPLE)) == []


def test_limit_one_returns_first_available():
    assert _run(SAMPLE, offset=3, limit=1) == ["line4"]


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_empty_source_returns_empty():
    assert _run([], limit=5, offset=2) == []


def test_generator_source_is_consumed_lazily():
    """Ensure the function works with a generator, not just lists."""
    gen = (f"l{i}" for i in range(5))
    assert _run(gen, offset=1, limit=2) == ["l1", "l2"]


# ---------------------------------------------------------------------------
# Validation errors
# ---------------------------------------------------------------------------

def test_negative_offset_raises():
    with pytest.raises(ValueError, match="offset"):
        _run(SAMPLE, offset=-1)


def test_zero_limit_raises():
    with pytest.raises(ValueError, match="limit"):
        _run(SAMPLE, limit=0)


def test_negative_limit_raises():
    with pytest.raises(ValueError, match="limit"):
        _run(SAMPLE, limit=-3)
