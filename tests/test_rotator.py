"""Tests for logslice.rotator."""

from __future__ import annotations

import os
import pytest

from logslice.archiver import ArchiveOptions
from logslice.rotator import RotateOptions, rotate_logs, _chunk


LINES = [f"2024-01-01 line {i}" for i in range(10)]


# ---------------------------------------------------------------------------
# _chunk helper
# ---------------------------------------------------------------------------

def test_chunk_by_lines():
    chunks = list(_chunk(LINES, max_lines=3, max_bytes=None))
    assert len(chunks) == 4  # 3+3+3+1
    assert chunks[0] == LINES[:3]
    assert chunks[-1] == LINES[9:]


def test_chunk_no_limits_single_chunk():
    chunks = list(_chunk(LINES, max_lines=None, max_bytes=None))
    assert len(chunks) == 1
    assert chunks[0] == LINES


def test_chunk_empty_input():
    assert list(_chunk([], max_lines=5, max_bytes=None)) == []


def test_chunk_by_bytes():
    # Each line is ~15 bytes; cap at 30 → ~2 lines per chunk
    chunks = list(_chunk(LINES[:6], max_lines=None, max_bytes=30))
    assert len(chunks) >= 2
    # All lines should be present
    flat = [l for c in chunks for l in c]
    assert flat == LINES[:6]


# ---------------------------------------------------------------------------
# rotate_logs integration
# ---------------------------------------------------------------------------

def test_rotate_single_file_when_no_limits(tmp_path):
    base = str(tmp_path / "out.log")
    opts = RotateOptions(archive=ArchiveOptions(format="none"))
    results = rotate_logs(LINES, base, opts)
    assert len(results) == 1
    _, count = results[0]
    assert count == len(LINES)


def test_rotate_creates_multiple_files(tmp_path):
    base = str(tmp_path / "out.log")
    opts = RotateOptions(
        max_lines=3,
        archive=ArchiveOptions(format="none"),
        name_template="{base}.{index}{ext}",
    )
    results = rotate_logs(LINES, base, opts)
    assert len(results) == 4  # 3+3+3+1
    total = sum(c for _, c in results)
    assert total == len(LINES)


def test_rotate_files_exist_on_disk(tmp_path):
    base = str(tmp_path / "out.log")
    opts = RotateOptions(
        max_lines=5,
        archive=ArchiveOptions(format="none"),
    )
    results = rotate_logs(LINES, base, opts)
    for path, _ in results:
        assert os.path.isfile(path)


def test_rotate_gz_compressed(tmp_path):
    base = str(tmp_path / "out.log")
    opts = RotateOptions(
        max_lines=4,
        archive=ArchiveOptions(format="gz"),
    )
    results = rotate_logs(LINES, base, opts)
    for path, _ in results:
        assert path.endswith(".gz")


def test_rotate_empty_input_returns_empty(tmp_path):
    base = str(tmp_path / "out.log")
    results = rotate_logs([], base)
    assert results == []


def test_rotate_default_opts(tmp_path):
    base = str(tmp_path / "out.log")
    results = rotate_logs(LINES[:2], base)
    assert len(results) == 1
