# woninet

A local network monitoring system.
It enumerates all candidate IP addresses in your /24 subnet and performs ARP + ICMP host detection to determine existence,
reachability, and latency. Metrics are collected continuously and processed through an alert engine.

**Note: This script requires sudo privileges.**

## Features

- **ARP + ICMP Host Detection** (Distinguishes real devices from nonexistent IPs and filters out Wi‑Fi ARP‑delay noise.)

- **Continuous Monitoring Loop**

- **Alert Engine** (Evaluates real‑time alert rules (e.g., latency thresholds))

- **Threaded Collectors**

- **Structured Device Model** (Tracks metadata such as last‑seen timestamp, MAC address (when available), reachability, and latency.)

- **In‑Memory Storage Engine**

- **Detailed Logging**

## Future Plans

- Pass latency limit and alert rules as command line argument.
- Add ARP table caching to further reduce Wi‑Fi latency noise.
- Optional SQLite storage for long‑term historical metrics.
- Accept defined IP and MAC addresses as command‑line arguments.
- Add looping for web dashboard.
- Send `reachability` and `existence` paramters to web dashboard.

## Known Issues

- No Persistent Storage Yet
- Monitoring Scope Limited to /24 Subnet

## How To Run

**Note:**

- *woninet* is under active development.
- PyPI releases will be published once the API stabilizes.

### 1. Clone the repository

```shell
git clone https://github.com/teymuri-alireza/woninet
cd woninet
```

### 2. Create and activate a virtual environment:

**Note:** Create the virtual environment outside the project directory to avoid
`Multiple top-level packages discovered in a flat-layout` errors.

```shell
python3 -m venv ../venv
source ../venv/bin/activate
```

### 3. Install woninet locally:

Until the PyPI release is available, install the package from the repository:

```shell
pip3 install .
```

### 4. Run woninet

```shell
sudo venv/bin/python3 -m woninet --version
```

## Requirements

- Unix-based operating systems
- Python >= 3.12
- ping3 v4.0.4 (pyhton3 module)
- Root privileges

## Documentation

if you have any question or need clarification, check the [documentation](./docs/documentation.md) guide.

## Contribution

Contributions are welcome. If you have a new feature in mind or have found a bug, please consider opening a pull request or an issue.

### What You Can Contribute

- Scan logic improvements
- Arguments, flags and CLI enhancements
- Code quality, structure or performance
- Fixes for typoes, grammar or documentation errors

### What not to contribute

Don't modify the version number. Versioning is handled by the maintainer after significant merges or changes.