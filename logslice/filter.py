"""Keyword and regex filtering for log lines."""

import re
from typing import Iterable, Iterator, Optional


def filter_lines(
    lines: Iterable[str],
    include: Optional[str] = None,
    exclude: Optional[str] = None,
    ignore_case: bool = False,
) -> Iterator[str]:
    """Yield lines that match *include* pattern and do not match *exclude* pattern.

    Parameters
    ----------
    lines:
        Source iterable of raw log lines.
    include:
        Regex pattern; only lines matching this pattern are kept.
        ``None`` means no inclusion filter (keep all).
    exclude:
        Regex pattern; lines matching this pattern are dropped.
        ``None`` means no exclusion filter (drop none).
    ignore_case:
        When ``True`` both patterns are compiled with ``re.IGNORECASE``.
    """
    flags = re.IGNORECASE if ignore_case else 0

    inc_re: Optional[re.Pattern] = re.compile(include, flags) if include else None
    exc_re: Optional[re.Pattern] = re.compile(exclude, flags) if exclude else None

    for line in lines:
        if inc_re is not None and not inc_re.search(line):
            continue
        if exc_re is not None and exc_re.search(line):
            continue
        yield line


def compile_filter(
    include: Optional[str] = None,
    exclude: Optional[str] = None,
    ignore_case: bool = False,
):
    """Return a single-argument callable that filters one line.

    Useful for integrating with pipeline stages that expect a predicate.
    Returns ``True`` if the line should be kept.
    """
    flags = re.IGNORECASE if ignore_case else 0
    inc_re: Optional[re.Pattern] = re.compile(include, flags) if include else None
    exc_re: Optional[re.Pattern] = re.compile(exclude, flags) if exclude else None

    def _keep(line: str) -> bool:
        if inc_re is not None and not inc_re.search(line):
            return False
        if exc_re is not None and exc_re.search(line):
            return False
        return True

    return _keep
