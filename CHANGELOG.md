# Changelog

All notable changes to this project will be documented in this file.

---

## [Unreleased]
### Added
- Implemented `uptime()` method in `NetworkMonitorCore` class.
- Implemented `database_health()` method in `NetworkMonitorCore` class to check database for connectivity and schema existence.
- Implemented `get_history_count()` method in `NetworkMonitorCore` class to retrieve number of stored items in the database.
- Completed the `/stats` API route.

### Changed
- Provided local Swagger UI assets (JavaScript, CSS, favicon) for the `/docs` route to allow offline loading.
- Prevented giving direct access to storage in `PingCollector`, by passing a variable of database devices instead of an instance of `StorageEngine` class.
- Switched from `return` to `yield` in `PingCollector` to store outputs in real-time, and handle outputs inside `engine.py`.

---

## [1.3.0] - 2026-05-02
### Added
- Implemented `logging.yaml` file to parse and apply log file output for web dashboard.
- Implemented `ColorFormatter` class in `logging.py` to apply ANSI color codes to console output.
- Added additional ARP scan when device is reachable but no MAC address is found in the ARP cache.
- Introduced the new `--arp-noise-limit` parameter to increase control over ARP noise limit.
- Implement SQLite database and update `StorageEngine` to manage database sessions and API.

### Changed
- Renamed logging variables to snake_case.
- Replaced static log filename with a CLI argument for specifying the log file path.

### Removed
- Remove redundant metrics field from the `Device` class.

### Fixed
- Introduced `SocketPermissionError` and raised it alongside `PermissionError` to ensure socket privilege failures are handled in `engine.py`.
- Prevented `SocketAddressError` from repeating in a loop.
- Prevented overwriting `device.mac` with `None` by adding an explicit `status.mac` check.

---

## [1.2.0] - 2026-04-23

> **Note:** Version 1.2.0 is the first officially recommended stable release of woninet.  
> Earlier 1.x versions are considered transitional while the architecture, naming, and packaging were being finalized.

### Added
- Implemented trace-level logging for increased verbosity when troubleshooting network behavior.
- Added package initialization and entry-point modules to support standardized imports and CLI entry.
- Implemented server dashboard using FastAPI for monitoring via a web interface.
- Added `pyproject.toml` and modern PEP 517/518 build configuration for building and distributing the package.
- Migrated ICMP implementation from `ping3` to `icmplib` for more robust and featureful ping handling.
- Formatted code using Ruff to enforce consistent style and linting rules.
- Added separated device and metric history for easier handling for CLI mode and web dashboard.
- Exposed the **MAC address** field in the web dashboard.

### Changed
- **BREAKING:** Renamed the project from `pymonitor` to `woninet`. Updated all imports and references accordingly.
- Improved the internal directory/package structure for clearer module boundaries and maintainability.
- Moved the contribution guide into `CONTRIBUTING.md` for better discoverability.
- Changed hardcoded static and templates paths in `app.py` using pathlib.Path class to prevent **File not found** error when installed from wheel.

### Removed
- Deleted the old `build.sh` installer in favor of modern packaging.
- Removed the old `requirements.txt` after switching to `pyproject.toml`-based dependency management.
- Removed unused static files.

---

## [1.1.0] - 2026-04-17
### Added
- Defined ARP-related variables in the Device class.
- Implemented `HostStatus` class to track device status.
- Merged ARP and ICMP scanning logic into `detect_host()` to provide unified host detection behavior.

### Changed
- Updated the `PingCollector` class to collect ARP + ICMP data and simplified output behavior.
- Renamed the `Subnet` class for clearer semantics (name now better reflects its responsibilities).
- Improved CLI argument handler descriptions for clearer help output.

---

## [1.0.1] - 2026-04-17
### Added
- Added comments and documentation for classes and functions to clarify their behavior and usage.

### Fixed
- Removed duplicate declaration of `clear_history()`.
- Made the for-loop structure more explicit in the `PingCollector` class.
- Moved `update_seen()` to occur after latency validation to ensure only valid responses are recorded.
- Gracefully handled `PermissionError` within `PingCollector` to avoid crashing when insufficient privileges are encountered.

---

## [1.0.0] - 2026-04-16
### Added
- Major refactor from function-based to class-based architecture for improved performance and readability.
- Implemented file output for logger.

### Changed
- Temporarily disabled server mode while the new architecture stabilizes.
- Improved error handling in `build.sh`.

### Removed
- Removed legacy settings and configuration modules.
- Removed unused argument options.

### Fixed
- None.

### Security
- None.

---

**Note:** Pre‑1.0.0 versions were experimental and are not listed here.
