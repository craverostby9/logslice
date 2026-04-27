"""Tests for logslice.writer."""

from __future__ import annotations

import sys
from io import StringIO
from pathlib import Path

import pytest

from logslice.writer import write_output


LINES = ["line one", "line two\n", "line three"]


def test_write_to_file(tmp_path: Path):
    dest = tmp_path / "out.log"
    count = write_output(LINES, dest)
    assert count == 3
    written = dest.read_text(encoding="utf-8").splitlines()
    assert written == ["line one", "line two", "line three"]


def test_write_creates_parent_dirs(tmp_path: Path):
    dest = tmp_path / "nested" / "dir" / "out.log"
    write_output(["hello"], dest)
    assert dest.exists()


def test_write_returns_line_count(tmp_path: Path):
    dest = tmp_path / "count.log"
    count = write_output(["a", "b", "c", "d"], dest)
    assert count == 4


def test_write_stdout(capsys):
    count = write_output(["alpha", "beta"], output_path=None)
    assert count == 2
    captured = capsys.readouterr()
    assert "alpha" in captured.out
    assert "beta" in captured.out


def test_write_stdout_newline_normalised(capsys):
    write_output(["no newline"], output_path=None)
    captured = capsys.readouterr()
    assert captured.out.endswith("\n")


def test_write_empty_source(tmp_path: Path):
    dest = tmp_path / "empty.log"
    count = write_output([], dest)
    assert count == 0
    assert dest.read_text() == ""
