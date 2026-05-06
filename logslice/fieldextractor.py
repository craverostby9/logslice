"""Field extraction utilities for structured (JSON/key=value) log lines."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, Iterable, Iterator, Optional

_KV_RE = re.compile(r'([\w.\-]+)=(?:"([^"]*)"|([^\s,]*))')


def _parse_json(line: str) -> Optional[Dict[str, Any]]:
    """Return parsed JSON object or None if the line is not JSON."""
    stripped = line.strip()
    if stripped.startswith("{"):
        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            return None
    return None


def _parse_kv(line: str) -> Dict[str, str]:
    """Return key=value pairs extracted from a log line."""
    return {
        m.group(1): m.group(2) if m.group(2) is not None else m.group(3)
        for m in _KV_RE.finditer(line)
    }


def extract_field(line: str, field: str) -> Optional[str]:
    """Extract a single *field* value from *line*.

    Tries JSON first, then key=value format.  Returns ``None`` when the
    field cannot be found.
    """
    parsed = _parse_json(line)
    if parsed is not None:
        value = parsed.get(field)
        return str(value) if value is not None else None
    kv = _parse_kv(line)
    return kv.get(field)


def extract_fields(
    lines: Iterable[str],
    fields: Iterable[str],
    missing: str = "",
) -> Iterator[Dict[str, str]]:
    """Yield a dict of extracted *fields* for every line in *lines*.

    Missing fields are replaced with *missing* (default empty string).
    """
    field_list = list(fields)
    for line in lines:
        row: Dict[str, str] = {}
        for field in field_list:
            value = extract_field(line, field)
            row[field] = value if value is not None else missing
        yield row
