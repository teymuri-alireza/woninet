# Changelog

All notable changes to this project will be documented in this file.

---

## [1.1.0] - 2026-04-17
### Added
- Define ARP-related variables in the Device class.
- Implement HostStatus class to track device status.
- Merge ARP and ICMP scanning logic into the detect_host().

### Changed
- Update the PingCollector class to collect ARP + ICMP data and clean up output behavior.
- Rename the Subnet class for clarity.
- Improve argument handler descriptions.

### Fixed
- None.

### Security
- None.

---

## [1.0.1] - 2026-04-17
### Added
- Add comments and documentaion for classes and functions.

### Fixed
- Remove duplicate declaration of clear_history().
- Make for-loop structure more explicit inside PingCollector class.
- Move update_seen() to occur after latency validation.
- Gracefully handle PermissionError within PingCollector.

### Security
- None.

---

## [1.0.0] - 2026-04-16
### Added
- Major refactor from function-based to class-based architecture for improved performance and readability.
- Implement file output for logger.

### Changed
- Temporarily disable server mode.
- Improve error handling in build.sh.

### Removed
- Remove settings and configuration modules.
- Remove unused arguments options.

### Fixed
- None.

### Security
- None.

---

**Note:** Since version 1.0.0 is the first stable version, earlier versions are not listed here.