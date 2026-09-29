"""Five predefined habits with four weeks of example tracking data.

The data doubles as the test fixture. Tracking starts on Monday 2026-08-03 and
covers four full weeks (28 days), ending on Sunday 2026-08-30.
"""
from datetime import date, datetime, time, timedelta
from typing import Dict, List

from .habit import Habit, Periodicity

START = date(2026, 8, 3)  # a Monday
DAYS = 28

# Days (offsets from START) on which a DAILY habit was NOT done.
_DAILY_MISSES: Dict[str, set] = {
    "Brush teeth": set(),
    "Exercise": {6, 13, 20, 27},
    "Read 20 pages": {9, 10, 24},
}
# Weeks (0-3) in which a WEEKLY habit was NOT done.
_WEEKLY_MISSES: Dict[str, set] = {
    "Weekly review": set(),
    "Call parents": {2},
}

#: Longest streaks contained in the sample data (used by the tests).
EXPECTED_LONGEST = {
    "Brush teeth": 28, "Exercise": 6, "Read 20 pages": 13,
    "Weekly review": 4, "Call parents": 2,
}


def predefined_habits() -> List[Habit]:
    """Build the five predefined habits (3 daily, 2 weekly) with sample data."""
    created = datetime.combine(START, time(7, 0))
    habits = []
    for name, task, misses in [
        ("Brush teeth", "Brush teeth for two minutes", _DAILY_MISSES["Brush teeth"]),
        ("Exercise", "Work out for 30 minutes", _DAILY_MISSES["Exercise"]),
        ("Read 20 pages", "Read 20 pages of a book", _DAILY_MISSES["Read 20 pages"]),
    ]:
        done = [datetime.combine(START + timedelta(days=d), time(8 + d % 10, 15))
                for d in range(DAYS) if d not in misses]
        habits.append(Habit(name, task, Periodicity.DAILY, created, done))
    for name, task, misses in [
        ("Weekly review", "Review goals and plan the week", _WEEKLY_MISSES["Weekly review"]),
        ("Call parents", "Call parents for a chat", _WEEKLY_MISSES["Call parents"]),
    ]:
        done = [datetime.combine(START + timedelta(days=7 * w + 6), time(18, 30))
                for w in range(DAYS // 7) if w not in misses]
        habits.append(Habit(name, task, Periodicity.WEEKLY, created, done))
    return habits
