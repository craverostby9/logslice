"""Tests for logslice.grouper."""

from __future__ import annotations

import re
from typing import List, Tuple

import pytest

from logslice.classifier import ClassifyOptions
from logslice.grouper import flatten_groups, group_by_label


def _run(
    lines: List[str],
    options: ClassifyOptions | None = None,
) -> List[Tuple[str, List[str]]]:
    return list(group_by_label(lines, options))


INFO_RULE = ("info", re.compile(r"\bINFO\b", re.IGNORECASE))
ERROR_RULE = ("error", re.compile(r"\bERROR\b", re.IGNORECASE))


# ---------------------------------------------------------------------------
# Basic grouping
# ---------------------------------------------------------------------------

def test_empty_input_returns_empty():
    assert _run([]) == []


def test_no_rules_single_group():
    lines = ["a", "b", "c"]
    groups = _run(lines)
    assert len(groups) == 1
    assert groups[0][0] == "other"
    assert groups[0][1] == lines


def test_consecutive_same_label_merged():
    opts = ClassifyOptions(rules=[INFO_RULE])
    lines = ["INFO first", "INFO second", "INFO third"]
    groups = _run(lines, opts)
    assert len(groups) == 1
    assert groups[0][0] == "info"
    assert len(groups[0][1]) == 3


def test_label_change_creates_new_group():
    opts = ClassifyOptions(rules=[INFO_RULE, ERROR_RULE])
    lines = [
        "INFO startup",
        "INFO ready",
        "ERROR boom",
        "ERROR still broken",
    ]
    groups = _run(lines, opts)
    assert len(groups) == 2
    assert groups[0][0] == "info"
    assert groups[1][0] == "error"


def test_alternating_labels_produce_alternating_groups():
    opts = ClassifyOptions(rules=[INFO_RULE, ERROR_RULE])
    lines = ["INFO a", "ERROR b", "INFO c", "ERROR d"]
    groups = _run(lines, opts)
    labels = [g[0] for g in groups]
    assert labels == ["info", "error", "info", "error"]
    for _, grp in groups:
        assert len(grp) == 1


def test_mixed_with_unmatched_lines():
    opts = ClassifyOptions(rules=[INFO_RULE])
    lines = ["INFO hello", "just noise", "INFO world"]
    groups = _run(lines, opts)
    labels = [g[0] for g in groups]
    assert labels == ["info", "other", "info"]


# ---------------------------------------------------------------------------
# flatten_groups round-trip
# ---------------------------------------------------------------------------

def test_flatten_groups_round_trip():
    opts = ClassifyOptions(rules=[INFO_RULE, ERROR_RULE])
    lines = ["INFO a", "ERROR b", "INFO c"]
    groups = list(group_by_label(lines, opts))
    recovered = list(flatten_groups(groups))
    assert recovered == lines


def test_flatten_empty_groups():
    assert list(flatten_groups([])) == []
