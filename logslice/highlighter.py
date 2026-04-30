"""Terminal colour highlighting for matched log lines."""
from __future__ import annotations

import re
from typing import Iterable, Iterator, List, Optional

# ANSI escape codes
_RESET = "\033[0m"
_COLOURS = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "bold": "\033[1m",
}


def _colourise(text: str, colour: str) -> str:
    """Wrap *text* with the ANSI escape sequence for *colour*."""
    code = _COLOURS.get(colour, "")
    if not code:
        return text
    return f"{code}{text}{_RESET}"


def highlight_lines(
    lines: Iterable[str],
    patterns: List[str],
    colour: str = "yellow",
    ignore_case: bool = False,
) -> Iterator[str]:
    """Yield each line, colouring sub-strings that match any of *patterns*.

    Parameters
    ----------
    lines:
        Source lines to process.
    patterns:
        List of regex patterns whose matches will be highlighted.
    colour:
        Named ANSI colour to apply (default ``"yellow"``).  Falls back to
        no colouring when the name is unrecognised.
    ignore_case:
        When *True* compile patterns with ``re.IGNORECASE``.
    """
    if not patterns:
        yield from lines
        return

    flags = re.IGNORECASE if ignore_case else 0
    compiled = [re.compile(p, flags) for p in patterns]

    for line in lines:
        result = line
        for regex in compiled:
            result = regex.sub(
                lambda m: _colourise(m.group(0), colour), result
            )
        yield result


def supports_colour(stream) -> bool:  # type: ignore[type-arg]
    """Return *True* when *stream* appears to be a colour-capable TTY."""
    try:
        import os
        return stream.isatty() and os.environ.get("TERM", "") != "dumb"
    except AttributeError:
        return False
