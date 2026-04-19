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

- **Simple `build.sh` Setup**

## Future Plans

- Pass latency limit and alert rules as command line argument.
- Add ARP table caching to further reduce Wi‑Fi latency noise.
- Optional SQLite storage for long‑term historical metrics.
- Web‑based dashboard for real‑time monitoring.
- Accept defined IP and MAC addresses as command‑line arguments.

## Known Issues

- No Persistent Storage Yet
- Monitoring Scope Limited to /24 Subnet

## How To Run

Clone the repo First.

```shell
git clone https://github.com/teymuri-alireza/woninet
cd woninet
```

### Installing from pip

(work in progress — the package will be available on PyPI soon)

### Run in a virtual envirenment

1. Create and activate a virtual environment:

```shell
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies and run woninet:

```shell
pip3 install -r requirements.txt
sudo venv/bin/python3 -m woninet --version
```

## Requirements

- Unix-based operating systems
- Python 3.8+
- ping3 v4.0.4 (pyhton3 module)
- Root privileges

## Documentaion

if you have any question or need clarification, check the [documentation](./documentation.md) guide.

## Contribution

Contributions are welcome. If you have a new feature in mind or have found a bug, please consider opening a pull request or an issue.

### What You Can Contribute

- Scan logic improvements
- Arguments, flags and CLI enhancements
- Code quality, structure or performance
- Fixes for typoes, grammar or documentation errors

### What not to contribute

Don't modify the version number. Versioning is handled by the maintainer after significant merges or changes.