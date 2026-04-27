"""Tests for logslice.formatter."""

from __future__ import annotations

import json
import pytest

from logslice.formatter import format_lines, SUPPORTED_FORMATS


SAMPLE = ["2024-01-01 00:00:01 INFO  hello\n", "2024-01-01 00:00:02 DEBUG world\n"]


def test_plain_passthrough():
    result = list(format_lines(SAMPLE, fmt="plain"))
    assert result == SAMPLE


def test_plain_with_line_numbers():
    result = list(format_lines(SAMPLE, fmt="plain", include_line_numbers=True))
    assert result[0].startswith("1: ")
    assert result[1].startswith("2: ")


def test_jsonl_each_line_valid_json():
    result = list(format_lines(SAMPLE, fmt="jsonl"))
    assert len(result) == 2
    for raw in result:
        record = json.loads(raw)
        assert "line" in record


def test_jsonl_with_line_numbers():
    result = list(format_lines(SAMPLE, fmt="jsonl", include_line_numbers=True))
    record = json.loads(result[0])
    assert record["n"] == 1


def test_json_single_array():
    result = list(format_lines(SAMPLE, fmt="json"))
    assert len(result) == 1
    records = json.loads(result[0])
    assert isinstance(records, list)
    assert len(records) == 2


def test_json_with_line_numbers():
    result = list(format_lines(SAMPLE, fmt="json", include_line_numbers=True))
    records = json.loads(result[0])
    assert records[0]["n"] == 1
    assert records[1]["n"] == 2


def test_unsupported_format_raises():
    with pytest.raises(ValueError, match="Unsupported format"):
        list(format_lines(SAMPLE, fmt="xml"))


def test_supported_formats_constant():
    assert "plain" in SUPPORTED_FORMATS
    assert "json" in SUPPORTED_FORMATS
    assert "jsonl" in SUPPORTED_FORMATS
