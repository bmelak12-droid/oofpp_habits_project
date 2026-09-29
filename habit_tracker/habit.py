"""Core domain model: the :class:`Habit` class and the :class:`Periodicity` enum."""
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import List, Optional


class Periodicity(str, Enum):
    """Supported habit periods."""

    DAILY = "daily"
    WEEKLY = "weekly"

    @classmethod
    def parse(cls, value: str) -> "Periodicity":
        """Convert a string such as ``"Daily"`` to a :class:`Periodicity`.

        :raises ValueError: if the value is not a supported periodicity.
        """
        try:
            return cls(str(value).strip().lower())
        except ValueError:
            allowed = ", ".join(p.value for p in cls)
            raise ValueError(f"Unknown periodicity {value!r}. Choose one of: {allowed}")


def period_index(periodicity: Periodicity, day: date) -> int:
    """Map a calendar day to the integer index of the period containing it.

    Daily periods are numbered by day, weekly periods by ISO week (Monday to
    Sunday). Consecutive periods have consecutive indices, which makes streak
    detection a simple "run of consecutive integers" problem.
    """
    if periodicity is Periodicity.DAILY:
        return day.toordinal()
    return (day.toordinal() - 1) // 7  # 0001-01-01 was a Monday


@dataclass
class Habit:
    """A task the user wants to complete once per period.

    :param name: unique, human readable identifier (e.g. ``"Brush teeth"``).
    :param task: the task specification (e.g. ``"Brush teeth for 2 minutes"``).
    :param periodicity: :class:`Periodicity` of the habit.
    :param created_at: when the habit was created.
    :param completions: timestamps at which the task was checked off.
    """

    name: str
    task: str
    periodicity: Periodicity
    created_at: datetime = field(default_factory=datetime.now)
    completions: List[datetime] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("A habit needs a non-empty name.")
        self.name = self.name.strip()
        if not isinstance(self.periodicity, Periodicity):
            self.periodicity = Periodicity.parse(self.periodicity)

    def check_off(self, when: Optional[datetime] = None) -> datetime:
        """Record a completion of the task and return its timestamp.

        :param when: completion time, defaults to now.
        :raises ValueError: if ``when`` lies before the habit was created.
        """
        when = when or datetime.now()
        if when < self.created_at:
            raise ValueError("A task cannot be completed before the habit was created.")
        self.completions.append(when)
        self.completions.sort()
        return when

    def is_completed_in_period_of(self, day: date) -> bool:
        """Return True if the task was checked off in the period containing ``day``."""
        target = period_index(self.periodicity, day)
        return any(period_index(self.periodicity, c.date()) == target for c in self.completions)
