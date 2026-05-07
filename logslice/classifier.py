"""Line classifier — assigns a category label to each log line based on
pattern rules supplied by the caller.

Each rule is a ``(label, pattern)`` pair where *pattern* is a compiled
regular expression (or a plain string that will be compiled).  The first
rule whose pattern matches a line wins; unmatched lines receive the
configurable *default_label* (``"other"`` by default).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable, Iterator, List, Optional, Tuple, Union

_Pattern = Union[str, re.Pattern]


@dataclass
class ClassifyOptions:
    rules: List[Tuple[str, _Pattern]] = field(default_factory=list)
    default_label: str = "other"
    tag_prefix: str = "["  # opening bracket for inline tag
    tag_suffix: str = "]"  # closing bracket for inline tag
    inline: bool = False   # when True, prepend label tag to each line


def _compile_rules(
    rules: List[Tuple[str, _Pattern]]
) -> List[Tuple[str, re.Pattern]]:
    compiled = []
    for label, pat in rules:
        if isinstance(pat, str):
            pat = re.compile(pat)
        compiled.append((label, pat))
    return compiled


def _classify_line(
    line: str,
    compiled_rules: List[Tuple[str, re.Pattern]],
    default_label: str,
) -> str:
    for label, pattern in compiled_rules:
        if pattern.search(line):
            return label
    return default_label


def classify_lines(
    lines: Iterable[str],
    options: Optional[ClassifyOptions] = None,
) -> Iterator[Tuple[str, str]]:
    """Yield ``(label, line)`` pairs for every line in *lines*.

    If *options.inline* is ``True`` the line is returned with a label
    tag prepended, otherwise the original line text is unchanged.
    """
    if options is None:
        options = ClassifyOptions()

    compiled = _compile_rules(options.rules)

    for line in lines:
        label = _classify_line(line, compiled, options.default_label)
        if options.inline:
            tag = f"{options.tag_prefix}{label}{options.tag_suffix} "
            yield label, tag + line
        else:
            yield label, line
