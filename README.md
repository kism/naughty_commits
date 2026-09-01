# Naughty Commits

See how many of your commits land outside work hours.

[![Lint](https://github.com/kism/naughtycommits/actions/workflows/check.yml/badge.svg?branch=main)](https://github.com/kism/naughtycommits/actions/workflows/check.yml)
[![Type Check](https://github.com/kism/naughtycommits/actions/workflows/check_types.yml/badge.svg?branch=main)](https://github.com/kism/naughtycommits/actions/workflows/check_types.yml)
[![Test](https://github.com/kism/naughtycommits/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/kism/naughtycommits/actions/workflows/test.yml)

## Install

```bash
uv tool install naughty-commits
```

Or run it without installing:

```bash
uvx naughty-commits
```

## Usage

```bash
naughty-commits [repo] [--start HOUR] [--end HOUR]
```

`repo` defaults to the current directory. Work hours default to 08:00-17:00, Monday to Friday.

```text
$ naughty-commits ~/src/naughtycommits
Total commits: 42
Work time (08:00-17:00, Mon-Fri): 11 (26%)
Free time: 31 (74%)
```

Commits reachable from `HEAD` are counted, each in the timezone it was made in.

## Development

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/).

```bash
uv sync --all-extras
```

| Task        | Command                |
| ----------- | ---------------------- |
| Lint        | `ruff check`           |
| Format      | `ruff format`          |
| Type check  | `ty check`             |
| Test        | `pytest`               |
| Coverage    | `./scripts/run-coverage.sh` |
| All of it   | `./scripts/run-ci-local.sh` |

Config for every tool lives in `pyproject.toml`.

## Releasing

Publishing uses [PyPI trusted publishing](https://docs.pypi.org/trusted-publishers/), so no API token is
stored in the repo. Configure `kism/naughtycommits`, workflow `publish.yml`, environment `pypi` as a
trusted publisher on PyPI once, then:

```bash
uv version --bump patch   # or minor / major
uv lock
git commit -am "Release v$(uv version --short)"
git tag "v$(uv version --short)"
git push --follow-tags
```

The tag push builds and publishes; the workflow fails if the tag does not match the version in
`pyproject.toml`.
