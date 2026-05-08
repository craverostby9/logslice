"""Tests for logslice.archiver."""

from __future__ import annotations

import gzip
import bz2
import os
import pytest

from logslice.archiver import (
    ArchiveOptions,
    archive_lines,
    read_archive,
)


LINES = ["2024-01-01 info hello", "2024-01-01 debug world", "2024-01-01 error oops"]


# ---------------------------------------------------------------------------
# ArchiveOptions.output_path
# ---------------------------------------------------------------------------

def test_output_path_gz_appends_suffix():
    opts = ArchiveOptions(format="gz")
    assert opts.output_path("/tmp/out.log") == "/tmp/out.log.gz"


def test_output_path_bz2_appends_suffix():
    opts = ArchiveOptions(format="bz2")
    assert opts.output_path("/tmp/out.log") == "/tmp/out.log.bz2"


def test_output_path_none_unchanged():
    opts = ArchiveOptions(format="none")
    assert opts.output_path("/tmp/out.log") == "/tmp/out.log"


def test_output_path_no_double_suffix():
    opts = ArchiveOptions(format="gz")
    assert opts.output_path("/tmp/out.log.gz") == "/tmp/out.log.gz"


# ---------------------------------------------------------------------------
# archive_lines + read_archive round-trips
# ---------------------------------------------------------------------------

def test_archive_gz_round_trip(tmp_path):
    dest = str(tmp_path / "out.log")
    opts = ArchiveOptions(format="gz")
    final, count = archive_lines(LINES, dest, opts)
    assert final == dest + ".gz"
    assert count == len(LINES)
    recovered = [l.rstrip("\n") for l in read_archive(final)]
    assert recovered == LINES


def test_archive_bz2_round_trip(tmp_path):
    dest = str(tmp_path / "out.log")
    opts = ArchiveOptions(format="bz2")
    final, count = archive_lines(LINES, dest, opts)
    assert final == dest + ".bz2"
    assert count == len(LINES)
    recovered = [l.rstrip("\n") for l in read_archive(final)]
    assert recovered == LINES


def test_archive_plain_round_trip(tmp_path):
    dest = str(tmp_path / "out.log")
    opts = ArchiveOptions(format="none")
    final, count = archive_lines(LINES, dest, opts)
    assert final == dest
    assert count == len(LINES)
    recovered = [l.rstrip("\n") for l in read_archive(final)]
    assert recovered == LINES


def test_archive_creates_parent_dirs(tmp_path):
    dest = str(tmp_path / "nested" / "deep" / "out.log")
    opts = ArchiveOptions(format="none")
    final, _ = archive_lines(LINES, dest, opts)
    assert os.path.isfile(final)


def test_archive_default_opts(tmp_path):
    dest = str(tmp_path / "out.log")
    final, count = archive_lines(LINES, dest)
    # default is gz
    assert final.endswith(".gz")
    assert count == len(LINES)


def test_archive_lines_without_newline(tmp_path):
    dest = str(tmp_path / "out.log")
    opts = ArchiveOptions(format="none")
    archive_lines(["no newline"], dest, opts)
    with open(dest) as fh:
        content = fh.read()
    assert content == "no newline\n"


def test_archive_empty_input(tmp_path):
    dest = str(tmp_path / "empty.log")
    opts = ArchiveOptions(format="none")
    final, count = archive_lines([], dest, opts)
    assert count == 0
    assert os.path.isfile(final)
