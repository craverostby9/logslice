"""Unit tests for logslice.parser."""

from datetime import datetime

import pytest

from logslice.parser import parse_timestamp


@pytest.mark.parametrize(
    "line, expected",
    [
        (
            "2024-01-15T13:45:00 INFO Starting service",
            datetime(2024, 1, 15, 13, 45, 0),
        ),
        (
            "2024-01-15T13:45:00.123 DEBUG message",
            datetime(2024, 1, 15, 13, 45, 0, 123000),
        ),
        (
            "2024-01-15 13:45:00,456 ERROR something failed",
            datetime(2024, 1, 15, 13, 45, 0, 456000),
        ),
        (
            "2024-01-15 13:45:00.789 WARN low memory",
            datetime(2024, 1, 15, 13, 45, 0, 789000),
        ),
        (
            "2024-01-15 13:45:00 INFO plain timestamp",
            datetime(2024, 1, 15, 13, 45, 0),
        ),
        (
            "    at com.example.App.run(App.java:42)",
            None,
        ),
        (
            "No timestamp here at all",
            None,
        ),
    ],
)
def test_parse_timestamp(line: str, expected):
    result = parse_timestamp(line)
    assert result == expected


def test_parse_timestamp_returns_datetime_instance():
    line = "2024-06-01 00:00:01 INFO boot"
    result = parse_timestamp(line)
    assert isinstance(result, datetime)


def test_parse_timestamp_none_on_garbage():
    assert parse_timestamp("") is None
    assert parse_timestamp("   ") is None
    assert parse_timestamp("Exception in thread main") is None
