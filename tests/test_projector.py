"""Tests for logslice.projector."""

from __future__ import annotations

import json

import pytest

from logslice.projector import project_lines


def _json_line(**kwargs) -> str:
    return json.dumps(kwargs)


def test_no_fields_yields_lines_unchanged():
    lines = ["raw line 1", "raw line 2"]
    assert list(project_lines(lines, [])) == lines


def test_single_field_extracted():
    lines = [_json_line(level="INFO", msg="ok")]
    result = list(project_lines(lines, ["level"]))
    assert result == ["INFO"]


def test_multiple_fields_joined_by_separator():
    lines = [_json_line(level="WARN", msg="slow", pid="7")]
    result = list(project_lines(lines, ["level", "msg"], separator=" | "))
    assert result == ["WARN | slow"]


def test_missing_field_uses_placeholder():
    lines = [_json_line(level="ERROR")]
    result = list(project_lines(lines, ["level", "host"], missing="n/a"))
    assert result == ["ERROR  n/a"]


def test_template_applied():
    lines = [_json_line(level="DEBUG", msg="trace")]
    result = list(
        project_lines(lines, ["level", "msg"], template="[{level}] {msg}")
    )
    assert result == ["[DEBUG] trace"]


def test_template_missing_key_falls_back_to_separator():
    # Template references a field not in *fields* list — falls back gracefully
    lines = [_json_line(level="INFO")]
    result = list(
        project_lines(
            lines, ["level"], template="{level} {nonexistent}", missing="-"
        )
    )
    # fallback: separator join
    assert result == ["INFO"]


def test_kv_lines_projected():
    lines = ['level=INFO msg="hello world" pid=5']
    result = list(project_lines(lines, ["level", "msg"]))
    assert result == ["INFO  hello world"]


def test_empty_input_returns_empty():
    assert list(project_lines([], ["level"])) == []


def test_default_separator_is_two_spaces():
    lines = [_json_line(a="x", b="y")]
    result = list(project_lines(lines, ["a", "b"]))
    assert result == ["x  y"]


def test_multiple_lines_all_projected():
    lines = [
        _json_line(level="INFO", msg="start"),
        _json_line(level="ERROR", msg="fail"),
    ]
    result = list(project_lines(lines, ["level", "msg"], separator=":"))
    assert result == ["INFO:start", "ERROR:fail"]
