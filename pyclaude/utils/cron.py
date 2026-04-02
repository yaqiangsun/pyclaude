"""
Cron expression parsing and next-run calculation.

Supports the standard 5-field cron subset:
  minute hour day-of-month month day-of-week

Field syntax: wildcard, N, step (star-slash-N), range (N-M), list (N,M,...).
All times are interpreted in the process's local timezone.
"""

import re
from typing import List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class CronFields:
    """Parsed cron fields."""
    minute: List[int]
    hour: List[int]
    day_of_month: List[int]
    month: List[int]
    day_of_week: List[int]


# Field ranges (min, max)
FIELD_RANGES = [
    (0, 59),   # minute
    (0, 23),   # hour
    (1, 31),   # dayOfMonth
    (1, 12),   # month
    (0, 6),    # dayOfWeek (0=Sunday)
]


def _expand_field(field: str, field_index: int) -> Optional[List[int]]:
    """Parse a single cron field into a sorted array of matching values.

    Supports: wildcard, N, star-slash-N (step), N-M (range), and comma-lists.

    Args:
        field: Cron field string
        field_index: Index of field (0-4)

    Returns:
        List of matching values, or None if invalid
    """
    min_val, max_val = FIELD_RANGES[field_index]
    out = set()

    for part in field.split(","):
        part = part.strip()

        # Wildcard or star-slash-N (step)
        step_match = re.match(r"^\*(?:/(\d+))?$", part)
        if step_match:
            step = int(step_match.group(1)) if step_match.group(1) else 1
            if step < 1:
                return None
            for i in range(min_val, max_val + 1, step):
                out.add(i)
            continue

        # Range (N-M)
        range_match = re.match(r"^(\d+)-(\d+)$", part)
        if range_match:
            start = int(range_match.group(1))
            end = int(range_match.group(2))
            if start < min_val or end > max_val or start > end:
                return None
            for i in range(start, end + 1):
                out.add(i)
            continue

        # Single value
        try:
            val = int(part)
            if val < min_val or val > max_val:
                return None
            out.add(val)
        except ValueError:
            return None

    return sorted(out)


def parse_cron(expression: str) -> Optional[CronFields]:
    """Parse a cron expression into fields.

    Args:
        expression: Cron expression string

    Returns:
        CronFields or None if invalid
    """
    parts = expression.strip().split()
    if len(parts) != 5:
        return None

    minute = _expand_field(parts[0], 0)
    hour = _expand_field(parts[1], 1)
    day_of_month = _expand_field(parts[2], 2)
    month = _expand_field(parts[3], 3)
    day_of_week = _expand_field(parts[4], 4)

    if None in (minute, hour, day_of_month, month, day_of_week):
        return None

    return CronFields(
        minute=minute,
        hour=hour,
        day_of_month=day_of_month,
        month=month,
        day_of_week=day_of_week,
    )


def get_next_run(cron: CronFields, after: Optional[datetime] = None) -> Optional[datetime]:
    """Calculate the next run time after the given datetime.

    Args:
        cron: Parsed cron fields
        after: Starting datetime (default: now)

    Returns:
        Next run datetime, or None if no valid time found
    """
    if after is None:
        after = datetime.now()

    # Simple implementation - check next 1000 days
    for _ in range(1000):
        # Check month
        if after.month not in cron.month:
            # Move to first day of next valid month
            next_month = min(m for m in cron.month if m > after.month)
            after = after.replace(month=next_month, day=1, hour=0, minute=0, second=0)
            continue

        # Check day of month and day of week
        if after.day not in cron.day_of_month or after.weekday() not in cron.day_of_week:
            after = after + timedelta(days=1)
            after = after.replace(hour=0, minute=0, second=0)
            continue

        # Check hour
        if after.hour not in cron.hour:
            next_hour = min(h for h in cron.hour if h > after.hour) if any(h > after.hour for h in cron.hour) else None
            if next_hour is not None:
                after = after.replace(hour=next_hour, minute=0, second=0)
            else:
                after = after + timedelta(days=1)
                after = after.replace(hour=0, minute=0, second=0)
            continue

        # Check minute
        if after.minute not in cron.minute:
            next_minute = min(m for m in cron.minute if m > after.minute) if any(m > after.minute for m in cron.minute) else None
            if next_minute is not None:
                after = after.replace(minute=next_minute, second=0)
            else:
                after = after + timedelta(hours=1)
                after = after.replace(minute=0, second=0)
            continue

        # All fields match
        return after

    return None


__all__ = ["CronFields", "parse_cron", "get_next_run"]