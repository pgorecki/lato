# Change Log

## [0.13.0] - 2025-02-20

### Breaking Changes

- Registering multiple handlers for the same `Command` or `Query` in a single module now raises `DuplicateHandlerError` (fixes #8)

### Added

- `lato.exceptions` module with all custom exceptions
- `DuplicateHandlerError(TypeError)` — raised on duplicate command/query handler registration
- `HandlerNotFoundError(LookupError)` — raised when no handler is found for an alias or message
- `UnknownDependencyError(KeyError)` — moved from `dependency_provider` to `exceptions`

## [0.12.4] - 2025-02-20

- Moved `pytest-asyncio` from runtime to dev dependencies (fixes #9, #10)

## [0.12.3] - 2025-02-20

- Fixed `__version__` in `lato/__init__.py` to match release version
- Removed EOL `pypy-3.8` from CI test matrix
- Fixed CI compatibility with Poetry 2.x (`poetry check --lock`)
- Pin Poetry 1.8.5 for Python 3.9 CI jobs
- Gate release workflow on Tests passing
- Updated release workflow to Python 3.12

## [0.12.0] - 2025-01-02

- Improved handling of async functions by `TransactionContext`. Will raise `TypeError` if sync middleware is used with async handler.

## [0.11.1] - 2024-05-29

- Fix type annotations in `ApplicationModule`

## [0.11.0] - 2024-03-24

- Change `composer()` signature from `compose(values)` to `compose(**kwargs)`

## [0.10.0] - 2024-03-17

### Added

- Add async support in `Application`. New methods: `call_async`, `execute_async`, `publish_async`
- Add async support in `TransactionContext`. New methods: `call_async`, `execute_async`, `publish_async`

## [0.9.0] - 2024-02-28

### Added

- Add Sphinx docs

### Changed

- Rename `Task` to `Command`
- Rename `Application.emit()` to `Application.publish()`
- Rename `TransactionContext.emit()` to `TransactionContext.publish()`
- Remove `Application.on()` decorator in favor of `Application.handler()`

## [0.8.0] - 2024-01-08

Early release.