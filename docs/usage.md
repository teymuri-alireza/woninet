# Usage

This guide explains common ways to run *woninet* and how to resolve common issues.

# 1. Running Modes

## CLI mode

The simplest way to run *woninet* in CLI is:

```shell
woninet
```

In this method, logging runs at the `INFO` level. Output is minimal, but warnings will
still appear if a metric exceeds a rule in the `AlertEngine`.

You can enable more verbose output using:

```shell
woninet -v # DEBUG level
woninet -vv # TRACE level
```

## Web Dashboard

You can serve *woninet* dashboard on port 8080 with:

```shell
woninet --serve
```

In this mode, core logging is set to ERROR to reduce unnecessary output.

---

# 2. Positional Arguments

Positional arguments provide quick access to database information from the CLI.

## List devices

Display all stored devices:

```shell
woninet device list
```

## Show Device Information

Display detailed information about a device by IP address,
including its current alert state and recent alert events:

```shell
woninet device show 192.168.1.10
```

---

# 3. Logging

Logs can be written to a file using the `-o` or `--output` parameter.
By default, logs are printed only to `stdout`

```shell
woninet -o logs.log
woninet --output logs.log
```

---

# 4. Issues and Troubleshooting

## ARP Noise Limit

The default value for the `--arp-noise-limit` paramter is 300.0 ms.
Devices with latency equal to or higher than this value are considered ARP noise and
will not be stored in the database.
If you are on a weak or unstable network, you may want to adjust this threshold.

**Examples:**

Stores all detected devices regardless of latency:

```shell
woninet --arp-noise-limit 0
```

Only considers devices with latency above 800.0 as ARP noise:

```shell
woninet --arp-noise-limit 800
```

## Database and Network Synchronization

The `SQLite` database identifies devices using a combination of MAC and IP addresses.
If you move *woninet* to a different network, the IP subnet will likely change (e.g.,
from `192.168.1.x` to `192.168.2.x`).

Using the same database across different subnets can lead to data inconsistency. Stale
records for devices that are not currently online may presist, and historical alert events
may no longer correctly correlate with the new network topology.

**Recommendation:** It is highly recommended to initialize a new database file when switching
to a different network to ensure data integrity. You can do this using:

```shell
woninet --db path_to_new_database
```

## Address Already in Use

The default port for server mode is `8080`. If *woninet* exits with an `Address already
in use` error, use a different port:

```shell
woninet -p 9090
```

---

If you encounter additional issues, feel free to open an issue on the
[woninet](https://github.com/teymuri-alireza/woninet) GitHub repository.
