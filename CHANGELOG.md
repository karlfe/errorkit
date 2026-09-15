# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-09-14
### Added
- `Severity` enum aligned to stdlib `logging` levels.
- `ErrorDef` dataclass: code, message template, default severity, tags, source.
- `ErrorRegistry`: catalog registration, per-code severity overrides,
  severity-wide and code-specific action dispatch.
- Plugin discovery via `importlib.metadata.entry_points` (group `errorkit.errors`).
- Built-in actions: `log_action`, `print_action`, `raise_action`, `exit_action`.
- Optional YAML config loader for severity overrides (`errorkit[yaml]`).
