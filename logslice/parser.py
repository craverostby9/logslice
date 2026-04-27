"""Log line timestamp parser for structured log files."""

import re
from datetime import datetime
from typing import Optional

# Common log timestamp patterns
TIMESTAMP_PATTERNS = [
    # ISO 8601: 2024-01-15T13:45:00.123Z or 2024-01-15T13:45:00+00:00
    (r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2}))', '%Y-%m-%dT%H:%M:%S'),
    # Common log format: 2024-01-15 13:45:00,123
    (r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+)', '%Y-%m-%d %H:%M:%S,%f'),
    # Common log format: 2024-01-15 13:45:00.123
    (r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)', '%Y-%m-%d %H:%M:%S.%f'),
    # Common log format: 2024-01-15 13:45:00
    (r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', '%Y-%m-%d %H:%M:%S'),
    # Apache/nginx: 15/Jan/2024:13:45:00 +0000
    (r'(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2} [+-]\d{4})', '%d/%b/%Y:%H:%M:%S %z'),
    # Syslog: Jan 15 13:45:00
    (r'([A-Z][a-z]{2} +\d{1,2} \d{2}:\d{2}:\d{2})', '%b %d %H:%M:%S'),
]


def parse_timestamp(line: str) -> Optional[datetime]:
    """Extract and parse the first recognizable timestamp from a log line.

    Args:
        line: A single log line string.

    Returns:
        A datetime object if a timestamp is found, otherwise None.
    """
    for pattern, fmt in TIMESTAMP_PATTERNS:
        match = re.search(pattern, line)
        if match:
            raw = match.group(1)
            # Normalize ISO 8601 Z suffix
            raw_normalized = raw.rstrip('Z').split('+')[0].split('-')[0] if 'T' in raw else raw
            try:
                if 'T' in raw:
                    # Handle ISO 8601 more robustly
                    raw_clean = re.sub(r'(Z|[+-]\d{2}:\d{2})$', '', raw)
                    base_fmt = '%Y-%m-%dT%H:%M:%S.%f' if '.' in raw_clean else '%Y-%m-%dT%H:%M:%S'
                    return datetime.strptime(raw_clean, base_fmt)
                return datetime.strptime(raw, fmt)
            except ValueError:
                continue
    return None
