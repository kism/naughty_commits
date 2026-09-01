"""Main entrypoint."""

import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path

from pygit2 import GitError, Repository

from .constants import PROGRAM_NAME, PROGRAM_NAME_WITH_VERSION

SATURDAY = 5  # datetime.weekday(), Monday is 0
DEFAULT_START_HOUR = 8
DEFAULT_END_HOUR = 17


def commit_datetimes(repo_path: Path) -> list[datetime]:
    """Datetimes of every commit reachable from HEAD, in the committer's own timezone."""
    repo = Repository(str(repo_path))
    return [
        datetime.fromtimestamp(commit.commit_time, tz=timezone(timedelta(minutes=commit.commit_time_offset)))
        for commit in repo.walk(repo.head.target)
    ]


def is_work_time(when: datetime, start_hour: int, end_hour: int) -> bool:
    """Whether a commit landed on a weekday inside working hours."""
    return when.weekday() < SATURDAY and start_hour <= when.hour < end_hour


def report(datetimes: list[datetime], start_hour: int, end_hour: int) -> str:
    """Render the work/free time breakdown."""
    total = len(datetimes)
    if total == 0:
        return "No commits found."

    work = sum(1 for when in datetimes if is_work_time(when, start_hour, end_hour))
    free = total - work

    return "\n".join(
        [
            f"Total commits: {total}",
            f"Work time ({start_hour:02d}:00-{end_hour:02d}:00, Mon-Fri): {work} ({work / total:.0%})",
            f"Free time: {free} ({free / total:.0%})",
        ]
    )


def _get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog=PROGRAM_NAME, description=PROGRAM_NAME_WITH_VERSION)
    parser.add_argument("repo", type=Path, nargs="?", default=Path.cwd(), help="Path to the git repository")
    parser.add_argument("--start", type=int, default=DEFAULT_START_HOUR, help="Hour the work day starts")
    parser.add_argument("--end", type=int, default=DEFAULT_END_HOUR, help="Hour the work day ends")
    return parser.parse_args()


def main() -> None:
    """Main entrypoint."""
    args = _get_args()
    try:
        datetimes = commit_datetimes(args.repo)
    except (GitError, KeyError) as exc:  # Not a repo, or HEAD is unborn
        msg = f"{args.repo}: {exc}"
        raise SystemExit(msg) from exc

    print(report(datetimes, args.start, args.end))


if __name__ == "__main__":
    main()  # pragma: no cover
