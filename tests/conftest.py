import pytest

from habit_tracker.fixtures import predefined_habits
from habit_tracker.storage import HabitStorage


@pytest.fixture
def habits():
    return predefined_habits()


@pytest.fixture
def store():
    s = HabitStorage(":memory:")
    yield s
    s.close()
