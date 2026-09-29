"""Analytics module, written in a functional style.

All functions are pure: they never modify their arguments, perform no I/O and
return new values. Sequences are processed with ``map``/``filter``/``reduce``
and comprehensions instead of mutable loops.
"""
from datetime import date, timedelta
from functools import reduce
from itertools import count, takewhile
from typing import Callable, Iterable, List, Sequence, Tuple

from .habit import Habit, Periodicity, period_index


# --- helpers -------------------------------------------------------------
def completed_periods(habit: Habit) -> List[int]:
    """Sorted, de-duplicated period indices in which ``habit`` was completed."""
    return sorted({period_index(habit.periodicity, c.date()) for c in habit.completions})


def _longest_run(indices: Sequence[int]) -> int:
    """Length of the longest run of consecutive integers in a sorted sequence."""

    def step(acc: Tuple[int, int, int], i: int) -> Tuple[int, int, int]:
        prev, current, best = acc
        current = current + 1 if prev is not None and i == prev + 1 else 1
        return (i, current, max(best, current))

    return reduce(step, indices, (None, 0, 0))[2] if indices else 0


# --- required analytics --------------------------------------------------
def all_habits(habits: Iterable[Habit]) -> List[Habit]:
    """Return all currently tracked habits."""
    return list(habits)


def habits_by_periodicity(habits: Iterable[Habit], periodicity: Periodicity) -> List[Habit]:
    """Return all habits that share the given periodicity."""
    return list(filter(lambda h: h.periodicity == periodicity, habits))


def longest_streak(habit: Habit) -> int:
    """Longest run of consecutive completed periods for one habit."""
    return _longest_run(completed_periods(habit))


def longest_streak_of_all(habits: Iterable[Habit]) -> Tuple[str, int]:
    """Return ``(habit name, streak)`` for the habit with the longest streak.

    Returns ``("", 0)`` if there are no habits.
    """
    pairs = list(map(lambda h: (h.name, longest_streak(h)), habits))
    return reduce(lambda a, b: b if b[1] > a[1] else a, pairs, ("", 0))


# --- additional analytics ------------------------------------------------
def current_streak(habit: Habit, today: date) -> int:
    """Streak that is still alive on ``today``.

    The running period may still be open, so an unfinished current period does
    not break the streak; it simply is not counted yet.
    """
    done = set(completed_periods(habit))
    start = period_index(habit.periodicity, today)
    start = start if start in done else start - 1
    return len(list(takewhile(lambda i: i in done, count(start, -1))))


def missed_periods(habit: Habit, start: date, end: date) -> int:
    """Number of periods between ``start`` and ``end`` (inclusive) without a completion.

    Periods that begin before ``habit.created_at`` are not counted.
    """
    days = (start + timedelta(days=n) for n in range((end - start).days + 1))
    first = period_index(habit.periodicity, habit.created_at.date())
    periods = {period_index(habit.periodicity, d) for d in days}
    relevant = filter(lambda p: p >= first, periods)
    done = set(completed_periods(habit))
    return len(list(filter(lambda p: p not in done, relevant)))


def struggle_ranking(habits: Iterable[Habit], start: date, end: date) -> List[Tuple[str, int]]:
    """Habits ordered by number of missed periods (worst first) in a date range."""
    ranked = map(lambda h: (h.name, missed_periods(h, start, end)), habits)
    return sorted(ranked, key=lambda pair: (-pair[1], pair[0]))


def streaks_report(habits: Iterable[Habit]) -> List[Tuple[str, int]]:
    """``(name, longest streak)`` for every habit, longest first."""
    return sorted(map(lambda h: (h.name, longest_streak(h)), habits), key=lambda p: (-p[1], p[0]))


def apply_filters(habits: Iterable[Habit], *predicates: Callable[[Habit], bool]) -> List[Habit]:
    """Keep habits satisfying every predicate (functional composition helper)."""
    return list(filter(lambda h: all(p(h) for p in predicates), habits))
