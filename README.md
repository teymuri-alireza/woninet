# woninet

A local network monitoring system.
It enumerates all candidate IP addresses in your /24 subnet and performs ARP + ICMP host detection to determine existence,
reachability, and latency. Metrics are collected continuously and processed through an alert engine.

**Note: This script requires sudo privileges.**

## Features

- **ARP + ICMP Host Detection** (Distinguishes real devices from nonexistent IPs and filters out Wi‑Fi ARP‑delay noise.)

- **Alert Engine** (Evaluates real‑time alert rules (e.g., latency thresholds))

- **Threaded Collectors**

- **SQLite database** (for devices, recorded metrics, alert states, and alert events.)

- **Positional Argument for easier access to the database from the CLI**

- **Detailed Logging**

## Future Plans

- Pass alert rules as command-line arguments.
- Add ARP table caching to further reduce Wi‑Fi latency noise.
- Accept MAC addresses as command‑line arguments.
- Fetch MAC address from database for offline devices.
- Enhance web dashboard UI:
    1. Define device-specific routes for each device.
    2. Add charts for overall status.

## Known Issues

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

**Unix/Linux note:** The `--copies` flag forces Python to copy the interpreter instead of using a symbolic link.
This is required because you will apply Linux capabilities directly to the Python binary in the virtual environment.

#### Linux/macOS

```shell
python3 -m venv --copies ../venv
source ../venv/bin/activate
```

#### Windows (PowerShell)

```shell
py -m venv ..\venv
..\venv\Scripts\Activate.ps1
```

### 3. Install woninet locally:

Until the PyPI release is available, install the package from the repository:

```shell
pip3 install .
```

### 4. Run woninet

**Unix/Linux only:** To allow raw ICMP without running as root, grant the required capability to the Python interpreter inside the virtual environment:

```shell
sudo setcap cap_net_raw=eip ../venv/bin/python3
```

Finally, run  woninet normally:

```shell
python3 -m woninet --version
```

**Alternative (not recommended):** You can run woninet with sudo instead of using setcap, but this is discouraged for security reasons:

```shell
sudo ../venv/bin/python3 -m woninet
```

## Usage

This [guide](./docs/usage.md) explains common ways to run *woninet* and how to resolve common issues.

## Requirements

- Python >= 3.12
- Root privileges

## Documentation

if you have any question or need clarification, check the [documentation](./docs/documentation.md) guide.

## Contribution

Thanks for considering contributing to *woninet!*
To help us maintain code quality, stability, and a predictable release process, please review and follow the guidelines in our [Contributing Guide.](./CONTRIBUTING.md)