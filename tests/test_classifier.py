"""Tests for logslice.classifier."""

from __future__ import annotations

import re
from typing import List, Tuple

import pytest

from logslice.classifier import ClassifyOptions, classify_lines


def _run(lines: List[str], options: ClassifyOptions | None = None) -> List[Tuple[str, str]]:
    return list(classify_lines(lines, options))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ERROR_RULE = ("error", re.compile(r"\bERROR\b", re.IGNORECASE))
WARN_RULE = ("warn", re.compile(r"\bWARN\b", re.IGNORECASE))
INFO_RULE = ("info", re.compile(r"\bINFO\b", re.IGNORECASE))


# ---------------------------------------------------------------------------
# Basic behaviour
# ---------------------------------------------------------------------------

def test_no_rules_all_default():
    lines = ["hello", "world"]
    results = _run(lines)
    assert all(label == "other" for label, _ in results)


def test_matching_rule_assigns_label():
    opts = ClassifyOptions(rules=[ERROR_RULE])
    results = _run(["2024-01-01 ERROR something broke"], opts)
    assert results[0][0] == "error"


def test_first_matching_rule_wins():
    # A line containing both WARN and ERROR should get the first-matched label.
    opts = ClassifyOptions(rules=[WARN_RULE, ERROR_RULE])
    results = _run(["WARN ERROR ambiguous line"], opts)
    assert results[0][0] == "warn"


def test_unmatched_line_gets_default_label():
    opts = ClassifyOptions(rules=[ERROR_RULE], default_label="unknown")
    results = _run(["just a regular log line"], opts)
    assert results[0][0] == "unknown"


def test_custom_default_label():
    opts = ClassifyOptions(rules=[], default_label="misc")
    results = _run(["anything"], opts)
    assert results[0][0] == "misc"


# ---------------------------------------------------------------------------
# String patterns (auto-compiled)
# ---------------------------------------------------------------------------

def test_string_pattern_compiled_automatically():
    opts = ClassifyOptions(rules=[("debug", r"DEBUG")])
    results = _run(["DEBUG verbose output"], opts)
    assert results[0][0] == "debug"


# ---------------------------------------------------------------------------
# Inline tagging
# ---------------------------------------------------------------------------

def test_inline_false_line_unchanged():
    opts = ClassifyOptions(rules=[ERROR_RULE], inline=False)
    original = "ERROR boom"
    results = _run([original], opts)
    assert results[0][1] == original


def test_inline_true_prepends_tag():
    opts = ClassifyOptions(rules=[ERROR_RULE], inline=True)
    results = _run(["ERROR boom"], opts)
    label, line = results[0]
    assert line.startswith(f"[{label}] ")


def test_inline_custom_brackets():
    opts = ClassifyOptions(
        rules=[INFO_RULE],
        inline=True,
        tag_prefix="<",
        tag_suffix=">",
    )
    results = _run(["INFO starting up"], opts)
    _, line = results[0]
    assert line.startswith("<info> ")


# ---------------------------------------------------------------------------
# Multiple lines
# ---------------------------------------------------------------------------

def test_mixed_lines_classified_correctly():
    opts = ClassifyOptions(rules=[ERROR_RULE, WARN_RULE, INFO_RULE])
    lines = [
        "INFO service started",
        "WARN disk usage high",
        "ERROR connection refused",
        "some unstructured text",
    ]
    labels = [label for label, _ in _run(lines, opts)]
    assert labels == ["info", "warn", "error", "other"]


def test_empty_input_returns_empty():
    assert _run([]) == []
