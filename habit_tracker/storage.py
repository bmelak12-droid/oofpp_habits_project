"""Persistence layer based on the built-in :mod:`sqlite3` module."""
import sqlite3
from datetime import datetime
from typing import List, Optional

from .habit import Habit, Periodicity

SCHEMA = """
CREATE TABLE IF NOT EXISTS habits (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,
    task        TEXT NOT NULL,
    periodicity TEXT NOT NULL CHECK (periodicity IN ('daily', 'weekly')),
    created_at  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS completions (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id     INTEGER NOT NULL REFERENCES habits(id) ON DELETE CASCADE,
    completed_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_completions_habit ON completions(habit_id);
"""


class HabitStorage:
    """Store and load :class:`~habit_tracker.habit.Habit` objects in SQLite.

    :param db_path: path of the database file; ``":memory:"`` gives a throw-away DB.
    """

    def __init__(self, db_path: str = "habits.db") -> None:
        self._conn = sqlite3.connect(db_path)
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._conn.executescript(SCHEMA)

    def close(self) -> None:
        """Close the database connection."""
        self._conn.close()

    def save_habit(self, habit: Habit) -> None:
        """Insert a new habit (with any completions it already has).

        :raises ValueError: if a habit with the same name already exists.
        """
        try:
            with self._conn:
                cur = self._conn.execute(
                    "INSERT INTO habits (name, task, periodicity, created_at) VALUES (?, ?, ?, ?)",
                    (habit.name, habit.task, habit.periodicity.value, habit.created_at.isoformat()),
                )
                self._conn.executemany(
                    "INSERT INTO completions (habit_id, completed_at) VALUES (?, ?)",
                    [(cur.lastrowid, c.isoformat()) for c in habit.completions],
                )
        except sqlite3.IntegrityError:
            raise ValueError(f"A habit named {habit.name!r} already exists.")

    def add_completion(self, name: str, when: datetime) -> None:
        """Persist one completion for the habit called ``name``.

        :raises KeyError: if the habit does not exist.
        """
        with self._conn:
            cur = self._conn.execute(
                "INSERT INTO completions (habit_id, completed_at) "
                "SELECT id, ? FROM habits WHERE name = ?",
                (when.isoformat(), name),
            )
        if cur.rowcount == 0:
            raise KeyError(name)

    def delete_habit(self, name: str) -> bool:
        """Delete a habit and its completions. Returns True if something was deleted."""
        with self._conn:
            cur = self._conn.execute("DELETE FROM habits WHERE name = ?", (name,))
        return cur.rowcount > 0

    def get_habit(self, name: str) -> Optional[Habit]:
        """Load one habit by name, or ``None`` if it does not exist."""
        return next((h for h in self.load_all() if h.name == name), None)

    def load_all(self) -> List[Habit]:
        """Load every habit including its completions."""
        habits = []
        for hid, name, task, per, created in self._conn.execute(
            "SELECT id, name, task, periodicity, created_at FROM habits ORDER BY id"
        ).fetchall():
            rows = self._conn.execute(
                "SELECT completed_at FROM completions WHERE habit_id = ? ORDER BY completed_at",
                (hid,),
            ).fetchall()
            habits.append(
                Habit(name, task, Periodicity(per), datetime.fromisoformat(created),
                      [datetime.fromisoformat(r[0]) for r in rows])
            )
        return habits

    def is_empty(self) -> bool:
        """True if no habits are stored."""
        return self._conn.execute("SELECT COUNT(*) FROM habits").fetchone()[0] == 0

    def clear(self) -> None:
        """Remove all data."""
        with self._conn:
            self._conn.execute("DELETE FROM completions")
            self._conn.execute("DELETE FROM habits")
