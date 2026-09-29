from datetime import date, datetime

import pytest

from habit_tracker.habit import Habit, Periodicity, period_index


def test_periodicity_parse():
    assert Periodicity.parse(" Daily ") is Periodicity.DAILY
    with pytest.raises(ValueError):
        Periodicity.parse("monthly")


def test_habit_requires_name():
    with pytest.raises(ValueError):
        Habit("  ", "task", Periodicity.DAILY)


def test_check_off_records_sorted_timestamps():
    h = Habit("Run", "Run 5k", Periodicity.DAILY, datetime(2026, 1, 1))
    h.check_off(datetime(2026, 1, 3, 9))
    h.check_off(datetime(2026, 1, 2, 9))
    assert h.completions == [datetime(2026, 1, 2, 9), datetime(2026, 1, 3, 9)]


def test_cannot_complete_before_creation():
    h = Habit("Run", "Run", Periodicity.DAILY, datetime(2026, 1, 5))
    with pytest.raises(ValueError):
        h.check_off(datetime(2026, 1, 1))


def test_weekly_period_index_runs_monday_to_sunday():
    monday, sunday, next_monday = date(2026, 8, 3), date(2026, 8, 9), date(2026, 8, 10)
    w = Periodicity.WEEKLY
    assert period_index(w, monday) == period_index(w, sunday)
    assert period_index(w, next_monday) == period_index(w, monday) + 1


def test_is_completed_in_period():
    h = Habit("Call", "Call", Periodicity.WEEKLY, datetime(2026, 8, 1))
    h.check_off(datetime(2026, 8, 5, 12))
    assert h.is_completed_in_period_of(date(2026, 8, 9))
    assert not h.is_completed_in_period_of(date(2026, 8, 10))
