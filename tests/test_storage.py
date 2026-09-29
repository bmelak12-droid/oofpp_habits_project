from datetime import datetime

import pytest

from habit_tracker.habit import Habit, Periodicity


def test_roundtrip(store, habits):
    for h in habits:
        store.save_habit(h)
    loaded = store.load_all()
    assert [h.name for h in loaded] == [h.name for h in habits]
    assert loaded[1].completions == habits[1].completions
    assert loaded[3].periodicity is Periodicity.WEEKLY


def test_duplicate_name_rejected(store):
    store.save_habit(Habit("A", "a", Periodicity.DAILY))
    with pytest.raises(ValueError):
        store.save_habit(Habit("A", "again", Periodicity.DAILY))


def test_add_completion_and_missing_habit(store):
    store.save_habit(Habit("A", "a", Periodicity.DAILY, datetime(2026, 1, 1)))
    store.add_completion("A", datetime(2026, 1, 2, 8))
    assert store.get_habit("A").completions == [datetime(2026, 1, 2, 8)]
    with pytest.raises(KeyError):
        store.add_completion("nope", datetime.now())


def test_delete_cascades(store):
    store.save_habit(Habit("A", "a", Periodicity.DAILY, datetime(2026, 1, 1), [datetime(2026, 1, 2)]))
    assert store.delete_habit("A") is True
    assert store.delete_habit("A") is False
    assert store.is_empty()
    assert store._conn.execute("SELECT COUNT(*) FROM completions").fetchone()[0] == 0
