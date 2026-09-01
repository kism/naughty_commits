"""Program metadata."""

from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

PROGRAM_NAME = Path(__file__).parent.name.replace("_", "-").lower()
PROGRAM_REPO_URL = "https://github.com/kism/naughtycommits"

try:
    PROGRAM_VERSION = version(PROGRAM_NAME)
except PackageNotFoundError:  # pragma: no cover
    PROGRAM_VERSION = "<unknown, please run uv sync>"

PROGRAM_NAME_WITH_VERSION = f"{PROGRAM_NAME} v{PROGRAM_VERSION}"
