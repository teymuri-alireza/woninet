# Changelog

All notable changes to this project will be documented in this file.

---

## [Unreleased]
### Added
- Implemented error handler for `OperationalError` for when database file can not be opened.
- Implemented `packet_loss` metric.
- Implemented `_evaluate_latency()` and `_evaluate_packet_loss()` in `alerts.py` to handle metric evaluations.
- Implemented `report_stats()` to handle the new `stats` positional argument.
- Implemented `packet_loss` in database `devices` table.

### Changed
- Removed `nullable` field from `datetime` in `AlertStateTable` and `AlertEventTable` to store state transition time from `warning` to `ok`.
- Changed log output argument from `--output` to `--logs` to prevent conflict with stats' `--output` argument.
- Enhanced frontend UI: added `packet loss` metric, search bar, recent alerts, average latency, and device count.

### Fixed
- Added specific ARP command and regex to parse the ARP output for both Windows and Unix-based operating systems in `collectors.py`.

---

## [1.5.0] - 2026-05-22
### Added
- Introduced a `--color` CLI argument to enable or disable colored console log output.
- Implemented `device` positional argument for easier access to the database from the CLI.
- Implemented `fetch_recent_alert_events()` in `alert_event_repository.py`
- Implemented `get_recent_alert_events()` in `storage.py`
- Implemented `classify_recent_alert_events()` in `engine.py`
- Implemented `recent_alert_events` field in the `/stats` API route.
- Implemented `--max-workers` argument to control number of workers used to send ICMP ping
- Implemented `read_arp_table()` in `collectors.py` for faster ARP scans
- Implemented and used `consecutive_checks` parameter in `AlertStateTable`, `AlertStateRepository`, and `AlertEngine`.
- Implemented `-i`, `--ip` to use user-provided IP addresses to scan.
- Implemented `detect_ip_range()` in `utilities/detect_ip_range.py` to detect if an IP address is provided as a range or as a single IP.
- Implemented `is_device_ip_valid()` in `utilities/ip_validator.py` to handle validation on IP addresses of the dictionary of candidate devices.
- Implemented `enumerate_range()` in `ManualIPEnumerator` class to handle enumeration for range of IP addresses.

### Changed
- Used function-based structure in `main.py` for clarity and to control codes from running at import time.
- Renamed `duration` parameter to `consecutive_checks` in `AlertRule` for clarity.
- Enhanced docstrings and add `Attributes` field for class docstrings.

### Fixed
- Moved `submit_to_history()` before type check condition in `main.py` to update latency for offline devices to 0.0.
- Prevented `AttributeError` by adding condition for checking monitor's attribution for the global monitor variable.
- Add exception handler for `ValueError` to handle the error gracfully.

---

## [1.4.0] - 2026-05-10
### Added
- Implemented `uptime()` method in `NetworkMonitorCore` class.
- Implemented `database_health()` method in `NetworkMonitorCore` class to check database for connectivity and schema existence.
- Implemented `count_resources()` method in `NetworkMonitorCore` class to retrieve number of stored items in the database.
- Completed the `/stats` API route.
- Prevented metrics from being removed after alert evaluation by defining the new `AlertStateTable` and `AlertEventTable` logic.
- Introduced the new `-p`, `--port` CLI argument to change the port number for web dashbaord.
- Introduced the new `--db` CLI argument to use a different path for the SQLite database.

### Changed
- Provided local Swagger UI assets (JavaScript, CSS, favicon) for the `/docs` route to allow offline loading.
- Prevented giving direct access to storage in `PingCollector`, by passing a variable of database devices instead of an instance of `StorageEngine` class.
- Switched from `return` to `yield` in `PingCollector` to store outputs in real-time, and handle outputs inside `engine.py`.
- Renamed variables and methods for clarity and readability

### Fixed
- Removed `session.commit()` from `DeviceRepository` and `MetricRepository` to move transaction control outside the repository layer.

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
