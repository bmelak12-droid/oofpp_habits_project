"""Command line interface: a simple interactive menu built with ``input()``."""
from datetime import date, datetime, timedelta

from . import analytics
from .fixtures import predefined_habits
from .habit import Habit, Periodicity
from .storage import HabitStorage

MENU = """
===== Habit Tracker =====
 1  Create a habit
 2  Complete (check off) a habit
 3  Delete a habit
 4  List all habits
 5  List habits by periodicity
 6  Longest streak of all habits
 7  Longest streak of one habit
 8  Struggle report (missed periods)
 9  Load the 5 predefined habits
 0  Exit"""


def choose_habit(store: HabitStorage):
    """Show the stored habits as a numbered list and return the one the user picks."""
    habits = store.load_all()
    if not habits:
        print("No habits yet. Create one or load the predefined habits.")
        return None
    for number, habit in enumerate(habits, start=1):
        print(f"  {number}. {habit.name} ({habit.periodicity.value})")
    answer = input("Habit number: ").strip()
    if answer.isdigit() and 1 <= int(answer) <= len(habits):
        return habits[int(answer) - 1]
    print("Invalid choice.")
    return None


def create_habit(store: HabitStorage) -> None:
    """Ask for name, task and periodicity, then store a new habit."""
    name = input("Name: ").strip()
    task = input("Task (e.g. Run 5 km): ").strip()
    period = input("Periodicity (daily/weekly): ").strip()
    try:
        store.save_habit(Habit(name, task, Periodicity.parse(period)))
    except ValueError as error:
        print(f"Error: {error}")
        return
    print(f"Created {period.lower()} habit '{name}'.")


def complete_habit(store: HabitStorage) -> None:
    """Check off a habit at the current time."""
    habit = choose_habit(store)
    if habit is None:
        return
    when = habit.check_off(datetime.now())
    store.add_completion(habit.name, when)
    print(f"Checked off '{habit.name}' at {when:%Y-%m-%d %H:%M}.")


def delete_habit(store: HabitStorage) -> None:
    """Delete a habit and its history."""
    habit = choose_habit(store)
    if habit is not None:
        store.delete_habit(habit.name)
        print(f"Deleted '{habit.name}'.")


def list_habits(store: HabitStorage) -> None:
    """Print all currently tracked habits."""
    habits = analytics.all_habits(store.load_all())
    if not habits:
        print("No habits found.")
    for habit in habits:
        print(f"{habit.name:<16} {habit.periodicity.value:<7} {habit.task}")


def list_by_periodicity(store: HabitStorage) -> None:
    """Print all habits that share one periodicity."""
    try:
        period = Periodicity.parse(input("Periodicity (daily/weekly): "))
    except ValueError as error:
        print(f"Error: {error}")
        return
    for habit in analytics.habits_by_periodicity(store.load_all(), period):
        print(f"{habit.name:<16} {habit.task}")


def show_longest_streak_of_all(store: HabitStorage) -> None:
    """Print every habit's longest streak and the overall winner."""
    habits = store.load_all()
    for name, length in analytics.streaks_report(habits):
        print(f"{name:<16} {length}")
    best, length = analytics.longest_streak_of_all(habits)
    if best:
        print(f"\nLongest streak overall: {best} ({length} periods)")


def show_longest_streak_of_one(store: HabitStorage) -> None:
    """Print the longest and current streak of one chosen habit."""
    habit = choose_habit(store)
    if habit is not None:
        print(f"{habit.name}: longest streak {analytics.longest_streak(habit)}, "
              f"current streak {analytics.current_streak(habit, date.today())}")


def show_struggle(store: HabitStorage) -> None:
    """Rank habits by missed periods in a time window."""
    try:
        days = int(input("Days to look back [30]: ").strip() or 30)
        end_text = input("Last day YYYY-MM-DD [today]: ").strip()
        end = datetime.strptime(end_text, "%Y-%m-%d").date() if end_text else date.today()
    except ValueError:
        print("Invalid number or date.")
        return
    for name, missed in analytics.struggle_ranking(store.load_all(), end - timedelta(days=days - 1), end):
        print(f"{name:<16} missed {missed}")


def load_predefined(store: HabitStorage) -> None:
    """Store the 5 predefined habits, skipping any that already exist."""
    for habit in predefined_habits():
        try:
            store.save_habit(habit)
        except ValueError:
            print(f"Skipped '{habit.name}' (already exists).")
    print("Predefined habits loaded.")


ACTIONS = {
    "1": create_habit,
    "2": complete_habit,
    "3": delete_habit,
    "4": list_habits,
    "5": list_by_periodicity,
    "6": show_longest_streak_of_all,
    "7": show_longest_streak_of_one,
    "8": show_struggle,
    "9": load_predefined,
}


def main(db_path: str = "habits.db") -> None:
    """Run the interactive menu until the user chooses 0."""
    store = HabitStorage(db_path)
    try:
        while True:
            print(MENU)
            choice = input("Choose: ").strip()
            if choice == "0":
                print("Goodbye!")
                break
            action = ACTIONS.get(choice)
            if action is None:
                print("Please choose a number from the menu.")
            else:
                action(store)
    finally:
        store.close()
