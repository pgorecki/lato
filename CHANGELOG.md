# Change Log

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