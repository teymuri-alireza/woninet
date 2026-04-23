# Changelog

All notable changes to this project will be documented in this file.

---

## [Unreleased]

---

## [1.2.0] - 2026-04-23

> **Note:** Version 1.2.0 is the first officially recommended stable release of woninet.  
> Earlier 1.x versions are considered transitional while the architecture, naming, and packaging were being finalized.

### Added
- Implement trace-level logging for increased verbosity when troubleshooting network behavior.
- Add package initialization and entry-point modules to support standardized imports and CLI entry.
- Implement server dashboard using FastAPI for monitoring via a web interface.
- Add `pyproject.toml` and modern PEP 517/518 build configuration for building and distributing the package.
- Migrate ICMP implementation from `ping3` to `icmplib` for more robust and featureful ping handling.
- Format code using Ruff to enforce consistent style and linting rules.
- Add separated device and metric history for easier handling for CLI mode and web dashboard.
- Send **MAC address** field to web dashboard.

### Changed
- **BREAKING:** Rename the project from `pymonitor` to `woninet`. Update all imports and references accordingly.
- Improve the internal directory/package structure for clearer module boundaries and maintainability.
- Move the contribution guide into `CONTRIBUTING.md` for better discoverability.
- Change hardcoded static and templates path in `app.py` with pathlib.Path class to prevent **File not found** error when installed from wheel.

### Removed
- Delete the old `build.sh` installer in favor of modern packaging.
- Remove the old `requirements.txt` after switching to `pyproject.toml`-based dependency management.
- Remove unused static files.

---

## [1.1.0] - 2026-04-17
### Added
- Define ARP-related variables in the Device class.
- Implement `HostStatus` class to track device status.
- Merge ARP and ICMP scanning logic into the `detect_host()` to provide unified host detection behavior.

### Changed
- Update the `PingCollector` class to collect ARP + ICMP data and simplify output behavior.
- Rename the `Subnet` class for clearer semantics (name now better reflects its responsibilities).
- Improve CLI argument handler descriptions for clearer help output.

---

## [1.0.1] - 2026-04-17
### Added
- Add comments and documentation for classes and functions to clarify their behavior and usage.

### Fixed
- Remove duplicate declaration of `clear_history()`.
- Make the for-loop structure more explicit inside `PingCollector` class.
- Move `update_seen()` to occur after latency validation to ensure only valid responses are recorded.
- Gracefully handle `PermissionError` within `PingCollector` to avoid crashing when insufficient privileges are encountered.

---

## [1.0.0] - 2026-04-16
### Added
- Major refactor from function-based to class-based architecture for improved performance and readability.
- Implement file output for logger.

### Changed
- Temporarily disable server mode while the new architecture stabilizes.
- Improve error handling in `build.sh`.

### Removed
- Remove legacy settings and configuration modules.
- Remove unused arguments options.

### Fixed
- None.

### Security
- None.

---

**Note:** Pre‑1.0.0 versions were experimental and are not listed here.
