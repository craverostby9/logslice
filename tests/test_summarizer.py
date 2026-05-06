"""Tests for logslice.summarizer."""

from __future__ import annotations

import pytest

from logslice.summarizer import SummaryOptions, summarize_lines


def _run(lines, **kwargs):
    opts = SummaryOptions(**kwargs) if kwargs else None
    it, summary = summarize_lines(iter(lines), opts)
    return list(it), summary


def test_yields_all_lines_unchanged():
    lines = ["hello world", "foo bar", "baz"]
    out, _ = _run(lines)
    assert out == lines


def test_total_line_count():
    lines = ["a", "b", "c", "d"]
    _, summary = _run(lines)
    assert summary.total_lines == 4


def test_empty_input():
    out, summary = _run([])
    assert out == []
    assert summary.total_lines == 0
    assert summary.top_terms == []


def test_matched_pattern_count():
    lines = ["ERROR something broke", "INFO all good", "ERROR again"]
    _, summary = _run(lines, count_pattern=r"ERROR")
    assert summary.matched_pattern == 2


def test_no_pattern_matched_is_zero():
    lines = ["INFO fine", "DEBUG verbose"]
    _, summary = _run(lines)
    assert summary.matched_pattern == 0


def test_top_terms_are_most_common():
    lines = ["apple banana apple", "apple cherry banana", "cherry cherry"]
    _, summary = _run(lines, top_n=2)
    terms = dict(summary.top_terms)
    assert terms["apple"] == 3
    assert terms["cherry"] == 3
    assert len(summary.top_terms) == 2


def test_top_n_limits_results():
    lines = ["aaa bbb ccc ddd eee fff ggg"]
    _, summary = _run(lines, top_n=3)
    assert len(summary.top_terms) <= 3


def test_group_by_field_json():
    lines = [
        '{"level": "ERROR", "msg": "oops"}',
        '{"level": "INFO", "msg": "ok"}',
        '{"level": "ERROR", "msg": "again"}',
    ]
    _, summary = _run(lines, group_by_field="level")
    assert summary.group_counts["ERROR"] == 2
    assert summary.group_counts["INFO"] == 1


def test_group_by_missing_field_skipped():
    lines = ['{"msg": "no level here"}', '{"level": "WARN", "msg": "hi"}']
    _, summary = _run(lines, group_by_field="level")
    assert "WARN" in summary.group_counts
    assert len(summary.group_counts) == 1


def test_summary_as_dict_keys():
    _, summary = _run(["hello world"])
    d = summary.as_dict()
    assert set(d.keys()) == {"total_lines", "matched_pattern", "top_terms", "group_counts"}


def test_summary_as_dict_values_serialisable():
    import json

    lines = ['{"svc": "web"}', '{"svc": "db"}']
    _, summary = _run(lines, group_by_field="svc")
    # Should not raise
    json.dumps(summary.as_dict())
