# Habit Tracker (OOFPP portfolio project)

A Python backend for a habit tracking app: users define **daily** and **weekly**
habits, check them off, and analyse their streaks from an interactive menu.

* **OOP** for the domain model (`Habit`, `Periodicity`, `HabitStorage`)
* **Functional programming** for analytics (pure functions, `map`/`filter`/`reduce`)
* **SQLite** (`sqlite3`, standard library) for persistence
* **Plain Python `input()` menu** for the CLI, **pytest** for the tests

## Requirements
Python 3.7 or newer. The app itself needs no extra libraries; `pytest` is only needed for the tests.

## Installation
```bash
git clone https://github.com/bmelak12-droid/oofpp_habits_project.git
cd oofpp_habits_project
python -m venv .venv
.venv\Scripts\activate           # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

## Run
```bash
python main.py
```
A menu appears; type a number and press Enter:

```
 1  Create a habit
 2  Complete (check off) a habit
 3  Delete a habit
 4  List all habits
 5  List habits by periodicity
 6  Longest streak of all habits
 7  Longest streak of one habit
 8  Struggle report (missed periods)
 9  Load the 5 predefined habits
 0  Exit
```
Habits are saved in `habits.db` (SQLite) in the current folder, so they are still
there next time. Delete that file to start from scratch.

### First steps
1. Choose **9** to load the 5 predefined habits (4 weeks of example data).
2. Choose **4** to list them, **6** to see the longest streaks.
3. Choose **1** to create your own habit: enter a name, a task and `daily` or `weekly`.
4. Choose **2** and pick the habit's number to check it off.
5. Choose **8** for the struggle report. For the sample data enter `28` days and the
   last day `2026-08-30`.

## How streaks work
A habit is *completed* in a period if it was checked off at least once in it.
Daily periods are calendar days; weekly periods run Monday to Sunday. A streak
is a run of consecutive completed periods; a period without a check-off breaks it.
The *current* streak stays alive while the running period is still open.

## Predefined habits (test fixture)
`habit_tracker/fixtures.py` contains 3 daily habits (*Brush teeth*, *Exercise*,
*Read 20 pages*) and 2 weekly habits (*Weekly review*, *Call parents*) with data for
2026-08-03 to 2026-08-30. Their expected longest streaks are 28, 6, 13, 4 and 2.

## Project layout
```
habit_tracker/
  habit.py       Habit class, Periodicity enum, period_index()
  storage.py     HabitStorage (SQLite)
  analytics.py   pure functional analytics
  fixtures.py    predefined habits + sample data
  cli.py         interactive menu (input())
tests/           pytest suite (habit, analytics, storage, CLI)
main.py          launcher (run: python main.py)
```

## Running the tests
```bash
python -m pytest -v
```

## Design notes
* Period indices turn "consecutive periods" into "consecutive integers", so streak
  detection is one `reduce` over a sorted sequence for both daily and weekly habits.
* Analytics never mutate habits and do no I/O, which makes them easy to test.
* The storage layer is the only code that touches the database.
