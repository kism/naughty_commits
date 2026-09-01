"""Fixtures shared by the whole test suite."""

import calendar
from pathlib import Path

import pygit2
import pytest

# 2025-01-06 is a Monday. 10:00 is inside work hours, 22:00 is not.
COMMIT_TIMES_UTC = [
    calendar.timegm((2025, 1, 6, 10, 0, 0, 0, 0, 0)),  # Monday, work
    calendar.timegm((2025, 1, 6, 22, 0, 0, 0, 0, 0)),  # Monday, free
    calendar.timegm((2025, 1, 11, 10, 0, 0, 0, 0, 0)),  # Saturday, free
]


@pytest.fixture
def repo_path(tmp_path: Path) -> Path:
    """A git repo containing one work-hours commit and two free-time commits, all in UTC."""
    repo = pygit2.init_repository(tmp_path / "repo")
    tree = repo.TreeBuilder().write()
    parents = []
    for commit_time in COMMIT_TIMES_UTC:
        who = pygit2.Signature("Tester", "tester@example.com", commit_time, 0)
        parents = [repo.create_commit("HEAD", who, who, "commit", tree, parents)]
    return Path(repo.workdir)
