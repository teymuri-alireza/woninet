# Changelog

All notable changes to this project will be documented in this file.

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
