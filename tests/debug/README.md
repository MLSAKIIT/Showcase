# Debug Scripts

This directory contains debug and diagnostic scripts that are **not** part of the automated test suite.

## Files to Move Here

The following files in `tests/` are debug/check scripts, not actual unit tests:
- `check_*.py` - Various diagnostic scripts
- `debug_*.py` - Debug utilities
- `run_test_script.py` - Manual test runner
- `share_code.py` - Code sharing utility

## Actual Test Files

Files prefixed with `test_` are actual pytest-compatible unit tests and should remain in `tests/`.

## Usage

These scripts are meant to be run manually for debugging:

```bash
# Run a debug script
python tests/debug/check_database.py

# Run a diagnostic check
python tests/debug/debug_config.py
```
