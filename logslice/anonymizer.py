"""anonymizer.py – redact or mask sensitive fields in log lines."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable, Iterator, List, Optional

# Built-in patterns for common sensitive data
_BUILTIN_PATTERNS: dict[str, str] = {
    "ipv4": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "email": r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b",
    "uuid": r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b",
    "bearer": r"(?i)bearer\s+[A-Za-z0-9\-._~+/]+=*",
    "credit_card": r"\b(?:\d[ \-]?){13,16}\b",
}


@dataclass
class AnonymizeOptions:
    """Configuration for the anonymizer."""

    # Named built-in patterns to activate (e.g. ["ipv4", "email"])
    builtins: List[str] = field(default_factory=list)
    # Additional raw regex patterns supplied by the caller
    patterns: List[str] = field(default_factory=list)
    # Replacement string; supports \\1 back-references if desired
    replacement: str = "<REDACTED>"
    # When True, compile patterns case-insensitively
    ignore_case: bool = False


def _compile(options: AnonymizeOptions) -> List[re.Pattern]:
    """Return compiled regex objects from *options*."""
    flags = re.IGNORECASE if options.ignore_case else 0
    compiled: List[re.Pattern] = []
    for name in options.builtins:
        if name not in _BUILTIN_PATTERNS:
            raise ValueError(f"Unknown built-in anonymizer pattern: {name!r}")
        compiled.append(re.compile(_BUILTIN_PATTERNS[name], flags))
    for raw in options.patterns:
        compiled.append(re.compile(raw, flags))
    return compiled


def _redact(line: str, patterns: List[re.Pattern], replacement: str) -> str:
    for pat in patterns:
        line = pat.sub(replacement, line)
    return line


def anonymize_lines(
    lines: Iterable[str],
    options: Optional[AnonymizeOptions] = None,
) -> Iterator[str]:
    """Yield each line with sensitive data replaced by *options.replacement*.

    If *options* is ``None`` or carries no patterns the lines are yielded
    unchanged, making the function safe to include unconditionally in a
    pipeline.
    """
    if options is None:
        yield from lines
        return

    patterns = _compile(options)
    if not patterns:
        yield from lines
        return

    for line in lines:
        yield _redact(line, patterns, options.replacement)
