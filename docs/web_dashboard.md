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

### Application Lifecycle Management

The FastAPI application manages the lifecycle of the shared `NetworkMonitorCore` instance using the `lifespan()` context manager

By centralizing monitor lifecycle control within `lifespan()`, the application guarantees consistent state management across all API routes.

## 3. Route Overview

Each API route serves a distinct operational purpose. Details are outlined below.

### /devices - Device Discovery

The `/devices` route invokes `list_devices()`, which calls the **device service** to enumerate all currently active network devices.

Internally:

- The `device_service` module uses `get_monitor_gracefully()` to obtain an instance of `NetworkMonitorCore` while avoiding circular import issues.
- The `monitor`'s `get_device_history()` method is invocked to collect a list of discovered devices.
- Discovered devices are returned as a structured JSON list to the dashboard.

This endpoint dynamically reflects real-time network topology.

### /stats — Network Statistics

The `/stats` route accesses `get_network_stats()` from the `stats_service` module to
retrieve basic network performance and status metrics.
This endpoint responds with a JSON object that includes the following sections:

1. **identity:** Basic service identification information.

- service: Name of the service.
- version: Current version of the service.
- server_ip: IP address of the server hosting the service.

2. **health:** Current status regarding system health and connectivity.

- engine_alive: Boolean indicating whether the database engine is running.
- database_connectivity: Status of the database connection (e.g., "ok" or "error").
- database_schema: Status of the database schema (e.g., "ok", "error", "unknown").

**Note:** The `databse_schema` returns "unknown" if `database_connectivity` fails.

3. **stats:** Metrics of the network monitoring system.

- devices_total: Total number of devices currently monitored.
- metrics_total: Total number of metrics collected.
- uptime_seconds: Total uptime of the service in seconds..

4. **recent_alert_events:** The last 10 alert events fetched from the database.

**Example Response:**

```json
{
  "identity": {
    "service": "woninet",
    "version": "1.4.0",
    "server_ip": "192.168.120.56",
  },
  "health": {
    "engine_alive": true,
    "database": {
        "connection": "ok",
        "schema": "ok",
    },
  },
  "stats": {
    "devices_total": 15,
    "metrics_total": 125,
    "uptime_seconds": 45685,
  },
  "recent_alert_events": [
    {
      "device_ip": "192.168.120.67",
      "id": 47,
      "metric": "latency_ms",
      "event_type": "recover",
      "value": 41.65,
      "timestamp": "2026-05-14T20:49:52.681306"
    },
    {
      "device_ip": "192.168.120.67",
      "id": 46,
      "metric": "latency_ms",
      "event_type": "trigger",
      "value": 259.642,
      "timestamp": "2026-05-14T20:49:52.681306"
    },
    {
      "device_ip": "192.168.120.85",
      "id": 45,
      "metric": "latency_ms",
      "event_type": "trigger",
      "value": 259.642,
      "timestamp": "2026-05-14T20:49:52.681306"
    },
  ]
}
```
