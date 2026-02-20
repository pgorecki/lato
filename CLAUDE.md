# Lato - AI Development Guide

## Project Overview

Lato is a Python microframework for building modular monoliths and loosely coupled applications. It implements CQRS patterns with Commands, Queries, and Events, dependency injection, and transaction contexts.

- **Author**: Przemyslaw Gorecki
- **License**: MIT
- **Docs**: https://lato.readthedocs.io
- **PyPI**: https://pypi.org/project/lato/

## Architecture

### Core Concepts

- **Application** (`lato/application.py`): Top-level entry point, extends `ApplicationModule`
- **ApplicationModule** (`lato/application_module.py`): Registers handlers, supports nested submodules
- **TransactionContext** (`lato/transaction_context.py`): Scoped context for handler execution with middleware support
- **DependencyProvider** (`lato/dependency_provider.py`): Automatic dependency injection by name or type
- **Messages** (`lato/message.py`): `Command`, `Query`, `Event` base classes (all extend `Message`)
- **Exceptions** (`lato/exceptions.py`): All custom exceptions in one place

### CQRS Rules

- **Command/Query**: One handler per message type per module. Registering a second raises `DuplicateHandlerError`. Multiple modules can each have one handler for the same Command/Query (results get composed).
- **Event**: Multiple handlers allowed per module (pub/sub pattern).

### Handler Dispatch

- `app.call(func_or_alias)` — invoke a single function or alias
- `app.execute(command)` — execute all handlers for a Command/Query, compose results
- `app.publish(event)` — publish to all Event handlers, return dict of results
- All three have `_async` variants

## Development

### Setup

```bash
poetry install --without examples
```

### Running Tests

```bash
poetry run python -m pytest -p no:sugar -q tests/
```

### Running Mypy

```bash
poetry run mypy lato
```

### Running Doctests

```bash
poetry run pytest --doctest-modules lato
```

### Building Docs

```bash
poetry run sphinx-build -b html docs docs/_build
```

### Pre-commit Hooks

The project uses pre-commit hooks: `isort`, `black`, `autoflake`, and type hint upgrades. If a commit fails due to hooks, re-stage the auto-fixed files and commit again (new commit, not amend).

## CI/CD

### Tests Workflow (`.github/workflows/tests.yml`)

- Triggers on: push to `main`, pull requests
- Matrix: Ubuntu/MacOS/Windows x Python 3.9/3.10/3.11/3.12
- Python 3.9 jobs use Poetry 1.8.5 (Poetry 2.x requires Python 3.10+)
- Python 3.10+ jobs use latest Poetry 2.x
- Lock file check: `poetry lock --check` (Poetry 1.x) or `poetry check --lock` (Poetry 2.x)

### Release Workflow (`.github/workflows/release.yml`)

- Triggers on: tag push matching `v*.*.*`
- Waits for Tests workflow to pass before publishing
- Uses Python 3.12 for build/publish
- Publishes to PyPI via `poetry publish`

## Release Process

1. Create a release branch (e.g. `release/0.13.0`)
2. Bump version in `pyproject.toml`, `lato/__init__.py`, and `CHANGELOG.md`
3. Update `poetry.lock` if dependencies changed (`poetry lock`)
4. Push branch, open PR, wait for tests to pass
5. Squash merge the PR
6. Pull main, tag (`git tag v0.13.0`), push tag
7. The tag push triggers the Release workflow

## Version Tracking

Version must be kept in sync in three places:
- `pyproject.toml` (`version = "..."`)
- `lato/__init__.py` (`__version__ = "..."`)
- `CHANGELOG.md` (new entry at top)

## Code Style

- Imports sorted by `isort`, formatted by `black`
- Type hints used throughout
- Custom exceptions inherit from the closest built-in (`TypeError`, `LookupError`, `KeyError`)
- All custom exceptions live in `lato/exceptions.py` and are exported from `lato/__init__`
- Docstrings use Sphinx `:param:`, `:return:`, `:raises:` format
