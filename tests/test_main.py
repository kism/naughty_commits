"""Tests for the report and the CLI."""

import argparse
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pygit2
import pytest

from naughty_commits import __main__


def test_commit_datetimes_uses_commit_offset(repo_path: Path) -> None:
    # TEST: Commits are read back in their own timezone, not the machine's.
    datetimes = __main__.commit_datetimes(repo_path)
    assert len(datetimes) == 3
    assert all(dt.tzinfo == UTC for dt in datetimes)


@pytest.mark.parametrize(
    ("when", "expected"),
    [
        (datetime(2025, 1, 6, 10, tzinfo=UTC), True),  # Monday 10:00
        (datetime(2025, 1, 6, 22, tzinfo=UTC), False),  # Monday 22:00
        (datetime(2025, 1, 6, 8, tzinfo=UTC), True),  # Start hour is inclusive
        (datetime(2025, 1, 6, 17, tzinfo=UTC), False),  # End hour is exclusive
        (datetime(2025, 1, 11, 10, tzinfo=UTC), False),  # Saturday
        (datetime(2025, 1, 12, 10, tzinfo=UTC), False),  # Sunday
    ],
)
def test_is_work_time(when: datetime, expected: bool) -> None:
    assert __main__.is_work_time(when, 8, 17) is expected


def test_report_empty() -> None:
    assert __main__.report([], 8, 17) == "No commits found."


def test_report_counts() -> None:
    datetimes = [
        datetime(2025, 1, 6, 10, tzinfo=UTC),
        datetime(2025, 1, 6, 22, tzinfo=UTC),
        datetime(2025, 1, 11, 10, tzinfo=UTC),
        datetime(2025, 1, 12, 10, tzinfo=UTC),
    ]
    out = __main__.report(datetimes, 8, 17)
    assert "Total commits: 4" in out
    assert "Work time (08:00-17:00, Mon-Fri): 1 (25%)" in out
    assert "Free time: 3 (75%)" in out


def test_report_honours_custom_hours() -> None:
    # TEST: A commit outside the default window counts as work with wider hours.
    datetimes = [datetime(2025, 1, 6, 22, tzinfo=UTC)]
    assert "Work time (08:00-23:00, Mon-Fri): 1 (100%)" in __main__.report(datetimes, 8, 23)


def test_main(repo_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture) -> None:
    mock_args = argparse.Namespace(repo=repo_path, start=8, end=17)
    monkeypatch.setattr(argparse.ArgumentParser, "parse_args", lambda self: mock_args)

    __main__.main()

    out = capsys.readouterr().out
    assert "Total commits: 3" in out
    assert "Work time (08:00-17:00, Mon-Fri): 1 (33%)" in out


def test_main_not_a_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mock_args = argparse.Namespace(repo=tmp_path, start=8, end=17)
    monkeypatch.setattr(argparse.ArgumentParser, "parse_args", lambda self: mock_args)

    # TEST: A bad path exits cleanly rather than raising a traceback at the user.
    with pytest.raises(SystemExit):
        __main__.main()


def test_main_empty_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pygit2.init_repository(tmp_path / "empty")
    mock_args = argparse.Namespace(repo=tmp_path / "empty", start=8, end=17)
    monkeypatch.setattr(argparse.ArgumentParser, "parse_args", lambda self: mock_args)

    # TEST: A repo with an unborn HEAD exits cleanly.
    with pytest.raises(SystemExit):
        __main__.main()


def test_get_args_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.argv", ["naughty-commits"])
    args = __main__._get_args()
    assert args.repo == Path.cwd()
    assert (args.start, args.end) == (8, 17)


def test_commit_datetimes_non_utc_offset(tmp_path: Path) -> None:
    """A commit made at +10:00 reads back as 09:00 local, not 23:00 UTC the day before."""
    repo = pygit2.init_repository(tmp_path / "repo")
    tree = repo.TreeBuilder().write()
    epoch = int(datetime(2025, 1, 5, 23, tzinfo=UTC).timestamp())
    who = pygit2.Signature("Tester", "tester@example.com", epoch, 600)
    repo.create_commit("HEAD", who, who, "commit", tree, [])

    (found,) = __main__.commit_datetimes(Path(repo.workdir))
    assert found.utcoffset() == timedelta(hours=10)
    assert (found.weekday(), found.hour) == (0, 9)  # Monday 09:00
    assert __main__.is_work_time(found, 8, 17)
