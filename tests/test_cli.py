import pytest

from habit_tracker import cli


def feed(monkeypatch, *answers):
    """Make input() return the given answers one after another."""
    it = iter(answers)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(it))


def test_create_and_list(store, monkeypatch, capsys):
    feed(monkeypatch, "Yoga", "Stretch", "daily")
    cli.create_habit(store)
    cli.list_habits(store)
    out = capsys.readouterr().out
    assert "Created daily habit 'Yoga'" in out and "Stretch" in out


def test_create_rejects_bad_periodicity_and_duplicates(store, monkeypatch, capsys):
    feed(monkeypatch, "Yoga", "x", "monthly")
    cli.create_habit(store)
    assert "Error" in capsys.readouterr().out
    feed(monkeypatch, "Yoga", "x", "daily", "Yoga", "x", "daily")
    cli.create_habit(store)
    cli.create_habit(store)
    assert "already exists" in capsys.readouterr().out


def test_complete_habit(store, monkeypatch, capsys):
    feed(monkeypatch, "Yoga", "x", "daily", "1")
    cli.create_habit(store)
    cli.complete_habit(store)
    assert len(store.get_habit("Yoga").completions) == 1
    assert "Checked off 'Yoga'" in capsys.readouterr().out


def test_delete_habit(store, monkeypatch):
    feed(monkeypatch, "Yoga", "x", "daily", "1")
    cli.create_habit(store)
    cli.delete_habit(store)
    assert store.is_empty()


def test_invalid_habit_number(store, monkeypatch, capsys):
    cli.load_predefined(store)
    feed(monkeypatch, "99")
    cli.complete_habit(store)
    assert "Invalid choice" in capsys.readouterr().out


def test_predefined_streaks_and_periodicity(store, monkeypatch, capsys):
    cli.load_predefined(store)
    cli.show_longest_streak_of_all(store)
    assert "Longest streak overall: Brush teeth (28 periods)" in capsys.readouterr().out
    feed(monkeypatch, "weekly")
    cli.list_by_periodicity(store)
    out = capsys.readouterr().out
    assert "Weekly review" in out and "Exercise" not in out


def test_struggle_report(store, monkeypatch, capsys):
    cli.load_predefined(store)
    capsys.readouterr()  # discard the "loaded" message
    feed(monkeypatch, "28", "2026-08-30")
    cli.show_struggle(store)
    lines = capsys.readouterr().out.splitlines()
    assert lines[0].startswith("Exercise") and "missed 4" in lines[0]


def test_main_loop_runs_and_exits(tmp_path, monkeypatch, capsys):
    feed(monkeypatch, "9", "4", "x", "0")
    cli.main(str(tmp_path / "t.db"))
    out = capsys.readouterr().out
    assert "Brush teeth" in out and "Please choose a number" in out and "Goodbye" in out
