# Web Dashboard

This section explains the sequence of operations performed to serve the web dashboard.

**Note:** To learn about the scanning logic check -> [Core Logic](./core_logic.md).

## 1. Determining the Source IP

*woninet* begins by identifying the local machine’s primary IPv4 address.

It does this by:

- Opening a dummy UDP socket
- Connecting to `8.8.8.8:80` (no data is sent)
- Reading the local address assigned to that connection

If the network is unreachable, Python raises a network error and the script terminates early.

This ensures the monitor only proceeds when the system has an active interface.

## 2. Initializing the Web Application

An instance of the **FastAPI** class is created to power the dashboard and provide RESTful endpoints.
This object defines and manages the following routes:

- `/devices`
- `/stats`
- `/health`
- `/ (root dashboard interface)`

The root route ("/") serves **dashboard.html**, which provides the main user interface for viewing devices and network health.

## 3. Route Overview

Each API route serves a distinct operational purpose. Details are outlined below.

### /devices - Device Discovery

The `/devices` route invokes `list_devices()`, which calls the **device service** to enumerate all currently active network devices.

Internally:

- The `device_service` module uses `get_monitor_gracefully()` to obtain an instance of `NetworkMonitorCore` while avoiding circular import issues.
- The `monitor` object is started once per request.
- Discovered devices are returned as a structured JSON list to the dashboard.

This endpoint dynamically reflects real-time network topology.

### /stats — Network Statistics

The `/stats` route accesses `get_network_stats()` from the `stats_service` module to retrieve basic network performance and status metrics.

**To be updated:**

Integrate live traffic counters, throughput analysis, and uptime information from the `NetworkMonitorCore` instance once the statistics logic is finalized.

### /health — System Health

The `/health` route (implemented in `system.py`) returns the health status of the main monitoring device and its local environment.

**To be updated:**

Extend health checks to include interface connectivity, packet loss detection, and real-time latency reports.