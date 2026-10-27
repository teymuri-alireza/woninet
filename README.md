# Woninet

[![PyPI version](https://img.shields.io/pypi/v/woninet)](https://pypi.org/project/woninet/)
[![Python](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/)
[![License](https://img.shields.io/pypi/l/woninet)](https://github.com/teymuri-alireza/woninet/blob/main/LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/woninet)](https://pypi.org/project/woninet/)

A local network monitoring system.

**Woninet** continuously monitors devices on a local network using ARP and ICMP probes. It enumerates candidate IP addresses in a /24 subnet, determines device availability, measures latency, packet loss, and jitter, stores metrics in database, and evaluates configurable alert rules in real time.

![Woninet dashboard](https://github.com/teymuri-alireza/woninet/blob/dev/public/img/woninet-dasboard.png)

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Platform Notes](#platform-notes)
- [Testing](#testing)
- [Known Issues](#known-issues)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

## Features

- **ARP + ICMP host detection.** Distinguishes real devices from nonexistent IP addresses and filters out Wi-Fi ARP-delay noise.
- **Alert engine.** Evaluates real-time alert rules, such as latency thresholds, against collected metrics.
- **Threaded collectors.** Sends ICMP probes concurrently using a configurable number of worker threads.
- **SQLite storage.** Persists devices, recorded metrics, alert states, and alert events.
- **Database access from the CLI.** Accepts a positional argument for easier access to the database.
- **Detailed logging.**

## Requirements

- Python 3.12 or later.
- Elevated network privileges, because ARP and ICMP probing use raw sockets. On Linux, either of the following satisfies this requirement:
  - the `cap_net_raw` capability granted to the Python interpreter (recommended, see [Installation](#installation)), or
  - root privileges (discouraged for security reasons).

## Quick Start

On Linux, the minimal path is:

```shell
python3 -m venv --copies venv
source venv/bin/activate
pip install woninet
sudo setcap cap_net_raw=eip venv/bin/python3
woninet --help
```

For Docker, macOS, Windows, and source installs, see [Installation](#installation).

## Installation

### Option 1: Install from PyPI

#### Linux (recommended: `icmplib` with `cap_net_raw`)

Create and activate a virtual environment. The `--copies` flag forces Python to copy the interpreter instead of symlinking it, which is required because the capability is applied directly to the interpreter binary:

```shell
python3 -m venv --copies venv
source venv/bin/activate
```

Install Woninet:

```shell
pip install woninet
```

Grant the required capability to the Python interpreter:

```shell
sudo setcap cap_net_raw=eip venv/bin/python3
```

Run Woninet:

```shell
woninet --help
```

#### Linux (fallback: system `ping`)

If you do not grant the capability, Woninet falls back to the system `ping` command. Create the environment without `--copies`:

```shell
python3 -m venv venv
source venv/bin/activate
pip install woninet
woninet --help
```

#### macOS and Windows

```shell
pip install woninet
woninet --help
```

See [Platform Notes](#platform-notes) for privilege considerations on these systems.

### Option 2: Docker (Linux only)

Clone the repository and run:

```shell
chmod +x build_docker.sh
sudo ./build_docker.sh
```

The script runs `docker compose up -d --build` and prints the device's private IP address to standard output so you can open the web interface in a browser.

To open Woninet manually, type device's private IP address with the default `8080` port in the browser.

### Option 3: Install from source

1. Clone the repository:

    ```shell
    git clone https://github.com/teymuri-alireza/woninet
    cd woninet
    ```

2. Create and activate a virtual environment **outside** the project directory to avoid `Multiple top-level packages discovered in a flat-layout` errors.

    Linux

    ```shell
    python3 -m venv --copies ../venv
    source ../venv/bin/activate
    ```

    Windows (PowerShell):

    ```powershell
    py -m venv ..\venv
    ..\venv\Scripts\Activate.ps1
    ```

3. Install Woninet locally:

   ```shell
   pip3 install .
   ```

4. Grant raw-socket access and run.

   **Linux:** grant the capability to the virtual environment's interpreter, then run Woninet:

   ```shell
   sudo setcap cap_net_raw=eip ../venv/bin/python3
   woninet --version
   ```

   Running with `sudo` instead is possible but discouraged for security reasons:

   ```shell
   sudo ../venv/bin/python3 -m woninet
   ```

   **macOS and Windows:** run `woninet --version` after installation.

## Configuration

Alert rules and monitoring settings are defined in a JSON file. Rename `config.example.json` to `config.json`; Woninet loads it at startup.

When installing from PyPI, `config.example.json` is not included, so Woninet creates a `config.json` file with default values.

To use a different configuration file, pass its path with the `--config` CLI flag.

### Example

```json
{
    "monitoring": {
        "arp_noise_limit": 300.0,
        "max_workers": 4
    },
    "database": "woninet.db",
    "target_ip_list": [
        "192.168.1.1", "192.168.1.10", "192.168.1.20-30"
    ],
    "alert_rules": [
        {
            "metric": "latency",
            "threshold": 100,
            "consecutive_checks": 3
        },
        {
            "metric": "packet_loss",
            "threshold": 0.0,
            "consecutive_checks": 1
        },
        {
            "metric": "jitter",
            "threshold": 40.0,
            "consecutive_checks": 3
        }
    ]
}
```

### Settings reference

#### Monitoring

| Key | Description |
|---|---|
| `arp_noise_limit` | Latency threshold in milliseconds used to filter ARP resolution noise. Set to `0` to disable filtering. Helps eliminate Wi-Fi latency spikes. |
| `max_workers` | Maximum number of worker threads used to send ICMP pings. Higher values may increase system load and latency. |

#### Database

| Key | Description |
|---|---|
| `database` | Path to the SQLite database file where metrics and alerts are stored. |

#### Target IP list

| Key | Description |
|---|---|
| `target_ip_list` | A single address, a list of addresses, or a range (for example `192.168.1.1-100`) to scan. Monitoring is currently limited to a /24 subnet (see [Known Issues](#known-issues)). |

#### Alert rules

| Key | Description |
|---|---|
| `metric` | The metric to evaluate: `latency`, `packet_loss`, or `jitter`. |
| `threshold` | The value that triggers the alert. |
| `consecutive_checks` | Number of consecutive evaluations required before the alert state changes. Higher values reduce false positives. |

#### Units and ranges

- **Latency:** thresholds are evaluated in milliseconds.
- **Jitter:** thresholds are evaluated in milliseconds.
- **Packet loss:** values are percentages in the range 0.0 to 100.0. A value of 100.0 indicates 100% packet loss, and a threshold of 0.0 triggers on any packet loss.

## Usage

See the [usage guide](https://github.com/teymuri-alireza/woninet/blob/main/docs/usage.md) for common ways to run Woninet and how to resolve common issues.

## Platform Notes

| Platform | Probing method | Privileges |
|---|---|---|
| Linux | `icmplib` (recommended) or system `ping` (fallback) | `cap_net_raw` on the interpreter, or root |
| macOS | Untested | Untested |
| Windows | Untested | Untested |

Woninet has been developed and tested on Linux. macOS and Windows have not been tested, so installation and behavior on those platforms are not guaranteed. Feedback and bug reports from users on these systems are welcome.

Docker deployment is available on Linux only.

## Testing

Install the optional test dependencies:

```shell
pip install -e ".[test]"
```

Then run:

```shell
pytest
```

The test suite currently focuses on API behavior and core logic and uses pytest for automated verification.

## Known Issues

- Monitoring is currently limited to a single /24 subnet.

## Documentation

For questions or clarification, see the [documentation](https://github.com/teymuri-alireza/woninet/blob/main/docs/documentation.md).

## Contributing

Thank you for considering a contribution to Woninet. To help maintain code quality, stability, and a predictable release process, please review the [Contributing Guide](https://github.com/teymuri-alireza/woninet/blob/main/CONTRIBUTING.md) before submitting changes.

## License

This project is licensed under the terms of the MIT license.
