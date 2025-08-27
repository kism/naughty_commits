"""Main entry point for the Naughty Commits tool."""

import argparse
from datetime import datetime
from pathlib import Path

from pygit2 import Repository

FRIDAY_DAY = 5
WORK_DAY_START_HOUR = 8
WORK_DAY_END_HOUR = 17

# Define the command
COMMAND = ["git", "log", "--format='%at'"]


def main() -> None:
    """Entry point for nauighty-commits."""
    # Run the command
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("repo", type=Path, default=Path.cwd(), help="Path to the git repository")
    args = arg_parser.parse_args()

    repo_path = args.repo
    repo = Repository(repo_path)
    committimes = [commit.commit_time for commit in repo.walk(repo.head.target)]

    nworkdays = 0
    nfreedays = 0
    for unix_time in committimes:
        # Convert Unix timestamp to datetime object
        dt = datetime.fromtimestamp(unix_time)

        # Check if it's a weekday (Monday=0, Sunday=6)
        if dt.weekday() < FRIDAY_DAY and WORK_DAY_START_HOUR <= dt.hour < WORK_DAY_END_HOUR:
            nworkdays = nworkdays + 1
        else:
            nfreedays = nfreedays + 1

    totalcommits = nfreedays + nworkdays
    print("Total commits: " + str(totalcommits))

    print("Commits during free time:" + str(nfreedays))
    result = nfreedays / totalcommits * 100
    print("Percent during free time:" + str(round(result)) + "%")

    print("Commits during work time:" + str(nworkdays))
    result = nworkdays / totalcommits * 100
    print("Percent during work time:" + str(round(result)) + "%")


if __name__ == "__main__":
    main()
