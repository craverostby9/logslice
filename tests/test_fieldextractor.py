"""Tests for logslice.fieldextractor."""

from __future__ import annotations

import json
import pytest

from logslice.fieldextractor import extract_field, extract_fields


# ---------------------------------------------------------------------------
# extract_field
# ---------------------------------------------------------------------------

def test_extract_field_from_json():
    line = json.dumps({"level": "INFO", "msg": "started", "pid": 42})
    assert extract_field(line, "level") == "INFO"


def test_extract_field_numeric_json_returns_string():
    line = json.dumps({"pid": 42})
    assert extract_field(line, "pid") == "42"


def test_extract_field_missing_json_returns_none():
    line = json.dumps({"level": "WARN"})
    assert extract_field(line, "msg") is None


def test_extract_field_from_kv():
    line = 'ts=2024-01-01T00:00:00Z level=ERROR msg="disk full"'
    assert extract_field(line, "level") == "ERROR"


def test_extract_field_kv_quoted_value():
    line = 'ts=2024-01-01T00:00:00Z msg="hello world"'
    assert extract_field(line, "msg") == "hello world"


def test_extract_field_kv_missing_returns_none():
    line = "level=INFO pid=99"
    assert extract_field(line, "host") is None


def test_extract_field_plain_line_returns_none():
    line = "2024-01-01 INFO some plain log message"
    assert extract_field(line, "level") is None


def test_extract_field_broken_json_falls_back_to_kv():
    # Broken JSON but contains key=value pairs
    line = '{broken json level=INFO'
    assert extract_field(line, "level") == "INFO"


# ---------------------------------------------------------------------------
# extract_fields
# ---------------------------------------------------------------------------

def test_extract_fields_yields_one_dict_per_line():
    lines = [
        json.dumps({"level": "INFO", "pid": 1}),
        json.dumps({"level": "ERROR", "pid": 2}),
    ]
    results = list(extract_fields(lines, ["level", "pid"]))
    assert len(results) == 2
    assert results[0]["level"] == "INFO"
    assert results[1]["pid"] == "2"


def test_extract_fields_missing_uses_default():
    lines = [json.dumps({"level": "DEBUG"})]
    results = list(extract_fields(lines, ["level", "host"]))
    assert results[0]["host"] == ""


def test_extract_fields_custom_missing_sentinel():
    lines = ["level=WARN"]
    results = list(extract_fields(lines, ["level", "host"], missing="N/A"))
    assert results[0]["host"] == "N/A"


def test_extract_fields_empty_input():
    assert list(extract_fields([], ["level"])) == []


def test_extract_fields_no_fields_yields_empty_dicts():
    lines = [json.dumps({"level": "INFO"})]
    results = list(extract_fields(lines, []))
    assert results == [{}]
