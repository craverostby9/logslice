"""Tests for logslice.anonymizer."""

from __future__ import annotations

import pytest

from logslice.anonymizer import AnonymizeOptions, anonymize_lines


def _run(lines, **kwargs):
    opts = AnonymizeOptions(**kwargs) if kwargs else None
    return list(anonymize_lines(lines, opts))


# ---------------------------------------------------------------------------
# No-op cases
# ---------------------------------------------------------------------------

def test_none_options_passthrough():
    lines = ["hello world", "no secrets here"]
    assert list(anonymize_lines(lines, None)) == lines


def test_empty_options_passthrough():
    lines = ["hello world"]
    result = list(anonymize_lines(lines, AnonymizeOptions()))
    assert result == lines


def test_empty_input_returns_empty():
    assert list(anonymize_lines([], AnonymizeOptions(builtins=["ipv4"]))) == []


# ---------------------------------------------------------------------------
# Built-in patterns
# ---------------------------------------------------------------------------

def test_ipv4_redacted():
    lines = ["connected from 192.168.1.42 at noon"]
    result = _run(lines, builtins=["ipv4"])
    assert "192.168.1.42" not in result[0]
    assert "<REDACTED>" in result[0]


def test_email_redacted():
    lines = ["user alice@example.com logged in"]
    result = _run(lines, builtins=["email"])
    assert "alice@example.com" not in result[0]
    assert "<REDACTED>" in result[0]


def test_uuid_redacted():
    lines = ["request id=123e4567-e89b-12d3-a456-426614174000 done"]
    result = _run(lines, builtins=["uuid"])
    assert "123e4567" not in result[0]


def test_bearer_token_redacted():
    lines = ["Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.payload.sig"]
    result = _run(lines, builtins=["bearer"])
    assert "eyJhbGciOiJIUzI1NiJ9" not in result[0]


def test_multiple_builtins_combined():
    lines = ["user bob@test.io from 10.0.0.1"]
    result = _run(lines, builtins=["ipv4", "email"])
    assert "bob@test.io" not in result[0]
    assert "10.0.0.1" not in result[0]


# ---------------------------------------------------------------------------
# Custom patterns
# ---------------------------------------------------------------------------

def test_custom_pattern_redacted():
    lines = ["token=supersecret123 used"]
    result = _run(lines, patterns=[r"supersecret\w+"])
    assert "supersecret123" not in result[0]
    assert "<REDACTED>" in result[0]


def test_custom_replacement_string():
    lines = ["ip 1.2.3.4 blocked"]
    result = _run(lines, builtins=["ipv4"], replacement="***")
    assert "***" in result[0]
    assert "1.2.3.4" not in result[0]


def test_unknown_builtin_raises():
    with pytest.raises(ValueError, match="Unknown built-in"):
        _run(["line"], builtins=["nonexistent"])


def test_multiple_occurrences_all_redacted():
    lines = ["from 1.1.1.1 to 2.2.2.2"]
    result = _run(lines, builtins=["ipv4"])
    assert "1.1.1.1" not in result[0]
    assert "2.2.2.2" not in result[0]


def test_ignore_case_flag():
    lines = ["Authorization: BEARER mytoken123"]
    result = _run(lines, builtins=["bearer"], ignore_case=True)
    assert "mytoken123" not in result[0]
