"""Integration-style tests for logslice.transforms.apply_transforms."""

from __future__ import annotations

from logslice.anonymizer import AnonymizeOptions
from logslice.leveler import LevelOptions
from logslice.splitter import SplitOptions, SplitRule
from logslice.transforms import TransformOptions, apply_transforms


def _run(lines, **kwargs):
    opts = TransformOptions(**kwargs)
    return list(apply_transforms(lines, opts))


LINES = [
    "INFO  service started",
    "DEBUG loop tick",
    "ERROR disk full",
    "WARN  memory low",
    "INFO  request ok",
]


def test_no_options_passthrough():
    assert _run(LINES) == LINES


def test_include_filter():
    result = _run(LINES, include=["ERROR"])
    assert result == ["ERROR disk full"]


def test_exclude_filter():
    result = _run(LINES, exclude=["DEBUG"])
    assert "DEBUG loop tick" not in result
    assert len(result) == 4


def test_level_filter():
    opts = LevelOptions(min_level="WARN")
    result = _run(LINES, level=opts)
    levels = [l.split()[0] for l in result]
    assert "DEBUG" not in levels
    assert "INFO" not in levels
    assert "ERROR" in levels
    assert "WARN" in levels


def test_dedup_consecutive():
    dupes = ["INFO a", "INFO a", "INFO b"]
    result = _run(dupes, dedup="consecutive")
    assert result == ["INFO a", "INFO b"]


def test_truncation():
    result = _run(["a" * 20], max_width=10, truncate_marker="...")
    assert len(result[0]) == 10
    assert result[0].endswith("...")


def test_pagination_limit():
    result = _run(LINES, limit=2)
    assert result == LINES[:2]


def test_pagination_offset():
    result = _run(LINES, offset=2)
    assert result == LINES[2:]


def test_split_keep_buckets():
    split_opts = SplitOptions(
        rules=[SplitRule(pattern=r"ERROR", bucket="errors")]
    )
    result = _run(LINES, split=split_opts, keep_buckets=["errors"])
    assert result == ["ERROR disk full"]


def test_anonymize_ipv4():
    lines = ["connect from 192.168.1.1 ok"]
    anon = AnonymizeOptions(redact_ip=True)
    result = _run(lines, anonymize=anon)
    assert "192.168.1.1" not in result[0]


def test_combined_filter_and_limit():
    result = _run(LINES, include=["INFO"], limit=1)
    assert len(result) == 1
    assert "INFO" in result[0]


def test_empty_input_returns_empty():
    assert _run([]) == []
