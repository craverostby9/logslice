"""Tests for logslice.sampler."""

from __future__ import annotations

import pytest

from logslice.sampler import sample_lines


def _lines(n: int) -> list[str]:
    return [f"line {i}\n" for i in range(1, n + 1)]


# ---------------------------------------------------------------------------
# every_nth
# ---------------------------------------------------------------------------

def test_every_nth_basic():
    result = list(sample_lines(_lines(6), every_nth=2))
    assert result == ["line 2\n", "line 4\n", "line 6\n"]


def test_every_nth_one_keeps_all():
    src = _lines(5)
    assert list(sample_lines(src, every_nth=1)) == src


def test_every_nth_larger_than_source():
    result = list(sample_lines(_lines(3), every_nth=10))
    assert result == []


def test_every_nth_invalid_raises():
    with pytest.raises(ValueError, match="every_nth"):
        list(sample_lines(_lines(5), every_nth=0))


# ---------------------------------------------------------------------------
# reservoir sampling
# ---------------------------------------------------------------------------

def test_reservoir_returns_at_most_k():
    result = list(sample_lines(_lines(100), reservoir_size=10, seed=42))
    assert len(result) <= 10


def test_reservoir_returns_all_when_source_smaller():
    src = _lines(5)
    result = list(sample_lines(src, reservoir_size=20, seed=0))
    assert sorted(result) == sorted(src)


def test_reservoir_reproducible_with_seed():
    src = _lines(50)
    r1 = list(sample_lines(src, reservoir_size=10, seed=7))
    r2 = list(sample_lines(src, reservoir_size=10, seed=7))
    assert r1 == r2


def test_reservoir_invalid_raises():
    with pytest.raises(ValueError, match="reservoir_size"):
        list(sample_lines(_lines(5), reservoir_size=0))


# ---------------------------------------------------------------------------
# passthrough (no sampling)
# ---------------------------------------------------------------------------

def test_no_sampling_passthrough():
    src = _lines(10)
    assert list(sample_lines(src)) == src


# ---------------------------------------------------------------------------
# mutual exclusion
# ---------------------------------------------------------------------------

def test_both_options_raises():
    with pytest.raises(ValueError, match="at most one"):
        list(sample_lines(_lines(10), every_nth=2, reservoir_size=5))
