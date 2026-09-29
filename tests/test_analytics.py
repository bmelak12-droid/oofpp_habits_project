from datetime import date, datetime

from habit_tracker import analytics
from habit_tracker.fixtures import EXPECTED_LONGEST
from habit_tracker.habit import Habit, Periodicity


def test_all_habits(habits):
    assert len(analytics.all_habits(habits)) == 5


def test_habits_by_periodicity(habits):
    daily = analytics.habits_by_periodicity(habits, Periodicity.DAILY)
    weekly = analytics.habits_by_periodicity(habits, Periodicity.WEEKLY)
    assert {h.name for h in daily} == {"Brush teeth", "Exercise", "Read 20 pages"}
    assert {h.name for h in weekly} == {"Weekly review", "Call parents"}


def test_longest_streak_per_habit(habits):
    for h in habits:
        assert analytics.longest_streak(h) == EXPECTED_LONGEST[h.name]


def test_longest_streak_of_all(habits):
    assert analytics.longest_streak_of_all(habits) == ("Brush teeth", 28)
    assert analytics.longest_streak_of_all([]) == ("", 0)


def test_multiple_completions_in_one_period_count_once():
    h = Habit("X", "x", Periodicity.DAILY, datetime(2026, 1, 1))
    for hour in (8, 12, 20):
        h.check_off(datetime(2026, 1, 1, hour))
    assert analytics.longest_streak(h) == 1


def test_no_completions_means_zero_streak():
    assert analytics.longest_streak(Habit("X", "x", Periodicity.DAILY)) == 0


def test_current_streak_alive_and_broken(habits):
    brush = habits[0]
    assert analytics.current_streak(brush, date(2026, 8, 30)) == 28
    assert analytics.current_streak(brush, date(2026, 8, 31)) == 28  # today still open
    assert analytics.current_streak(brush, date(2026, 9, 2)) == 0     # broken


def test_struggle_ranking(habits):
    ranking = analytics.struggle_ranking(habits, date(2026, 8, 3), date(2026, 8, 30))
    assert dict(ranking) == {"Brush teeth": 0, "Exercise": 4, "Read 20 pages": 3,
                             "Weekly review": 0, "Call parents": 1}
    assert ranking[0][0] == "Exercise"


def test_missed_periods_ignores_time_before_creation():
    h = Habit("X", "x", Periodicity.DAILY, datetime(2026, 8, 10, 8))
    assert analytics.missed_periods(h, date(2026, 8, 1), date(2026, 8, 12)) == 3


def test_analytics_are_pure(habits):
    before = [list(h.completions) for h in habits]
    analytics.longest_streak_of_all(habits)
    analytics.struggle_ranking(habits, date(2026, 8, 3), date(2026, 8, 30))
    assert before == [h.completions for h in habits]
