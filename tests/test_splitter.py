"""Tests for logslice.splitter."""

from __future__ import annotations

import pytest

from logslice.splitter import (
    SplitOptions,
    SplitRule,
    iter_split,
    split_lines,
)


def _rules(*pairs: tuple) -> list:
    return [SplitRule(pattern=p, bucket=b) for p, b in pairs]


def test_no_rules_all_go_to_default():
    lines = ["alpha", "beta", "gamma"]
    result = split_lines(lines)
    assert result == {"default": lines}


def test_matching_rule_assigns_bucket():
    opts = SplitOptions(rules=_rules((r"ERROR", "errors")))
    lines = ["INFO ok", "ERROR boom", "INFO fine"]
    result = split_lines(lines, opts)
    assert result["errors"] == ["ERROR boom"]
    assert result["default"] == ["INFO ok", "INFO fine"]


def test_first_matching_rule_wins():
    opts = SplitOptions(
        rules=_rules((r"ERROR", "errors"), (r"ERROR", "also_errors"))
    )
    lines = ["ERROR x"]
    result = split_lines(lines, opts)
    assert "errors" in result
    assert "also_errors" not in result


def test_multiple_buckets():
    opts = SplitOptions(
        rules=_rules((r"ERROR", "errors"), (r"WARN", "warnings"))
    )
    lines = ["ERROR a", "WARN b", "INFO c"]
    result = split_lines(lines, opts)
    assert result["errors"] == ["ERROR a"]
    assert result["warnings"] == ["WARN b"]
    assert result["default"] == ["INFO c"]


def test_custom_default_bucket():
    opts = SplitOptions(default_bucket="misc")
    result = split_lines(["hello"], opts)
    assert "misc" in result
    assert result["misc"] == ["hello"]


def test_ignore_case_flag():
    opts = SplitOptions(
        rules=_rules((r"error", "errors")),
        ignore_case=True,
    )
    result = split_lines(["ERROR big problem"], opts)
    assert result.get("errors") == ["ERROR big problem"]


def test_empty_input_returns_empty_dict():
    result = split_lines([])
    assert result == {}


def test_iter_split_yields_pairs():
    opts = SplitOptions(rules=_rules((r"ERROR", "errors")))
    pairs = list(iter_split(["ERROR x", "INFO y"], opts))
    assert pairs == [("errors", "ERROR x"), ("default", "INFO y")]


def test_iter_split_no_options():
    pairs = list(iter_split(["a", "b"]))
    assert all(bucket == "default" for bucket, _ in pairs)


def test_split_preserves_order_within_bucket():
    opts = SplitOptions(rules=_rules((r"ERROR", "errors")))
    lines = ["ERROR 1", "ERROR 2", "ERROR 3"]
    result = split_lines(lines, opts)
    assert result["errors"] == ["ERROR 1", "ERROR 2", "ERROR 3"]
