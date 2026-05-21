# Core Logic

This section explains the full sequence of operations *woninet* performs to scan and
monitor the local network.

## 1. Determining the Source IP

*woninet* begins by identifying the local machine’s primary IPv4 address.

It does this by:

- Opening a dummy UDP socket
- Connecting to `8.8.8.8:80` (no data is sent)
- Reading the local address assigned to that connection

If the network is unreachable, Python raises a network error and the script terminates early.

This ensures the monitor only proceeds when the system has an active interface.

## 2. Initializing the Monitoring Core

An instance of NetworkMonitorCore is created.

The core receives:

- The source IP address
- Initial settings (intervals, alert rule)
- The full state containers (devices, history, alerts)
- The arp-noise-limit parameter, which will be passed to PingCollector instance.

The core is responsible for orchestrating:

- Subnet enumeration
- Host detection
- Metric collection
- Data storage
- Alert evaluation
- Logging

It is the central controller of the system.

## 3. Subnet Enumeration (/24 Range)

*woninet* uses the SubnetEnumerator class to generate a dictionary of candidate devices
within the local `/24` subnet.

For a source IP such as:

```text
192.168.1.23
```

It builds the full CIDR block:

```text
192.168.1.1 - 192.168.1.254
```

This step doesn't determine if devices exist or respond — it only constructs the list of
potential addresses.

The output is a dictionary:

```text
{ "192.168.1.1": Device(...), "192.168.1.2": Device(...), ... }
```

Every IP in the `/24` block is represented as a Device model with initial default values.

## 4. ARP + ICMP Host Detection

For each candidate device, a two‑stage detection pipeline runs:

### Stage A — ARP Check

*woninet* checks the system ARP table to see if the target IP already has a known MAC address.

This determines:

- Does this IP belong to a real existing device on the LAN?
- Has the device responded to ARP recently?
- Can the system discover a MAC address?

If ARP fails, the device is marked as:

```text
exists = False
```

If ICMP scan returns a valid result for the following IP address, another ARP scan is
performed to prevent stale ARP cache.

### Stage B — ICMP Ping

*woninet* sends an ICMP ping using `icmplib`.

Latency is interpreted carefully:

- latency < arp-noise-limit → valid response
- latency ≥ arp-noise-limit → considered "ARP delay noise," treated as unreachable

**Note:** The `--arp-noise-limit` parameter is passed via CLI argument and has the
default value of 300.0.

## 5. History Storage

The StorageEngine manages the database session and handles the database API:

### Current database tables:

- Device Table (device discoveries and status updates)
- Metric Table (device IP, metric name (e.g, latency), and value)

### 1. Device Table

Each device-related update is stored as a Device class, containing:

- Unique ID
- IP address
- MAC address
- Latency
- last_seen

The `Device` class has 2 more additional fields which are used in the scanning logic only:

- exists
- reachable

### 2. Metric Table

Each valid measurement (ARP-confirmed + reachability) is stored as a MetricRecord, containing:

- Unique ID
- IP address
- Metric
- value
- timestamp

### 3. Alert State Table

Each unique IP and metric is stored as an `AlertStateTable`, containing:

- Unique ID
- IP address
- metric
- state
- triggered_at

### 4. Alert Event Table

Each alert evaluation event is stored as an `AlertEventTable`, containing:

- Unique ID
- IP address
- metric
- value
- event_type
- timestamp

## 6. Alert Engine Evaluation

Captured device metrics are passed to the `AlertEngine` in real-time for evaluation.

During the `evaluate()` process, the current alert state of the `(device_ip, metric)`
pair  is retrieved from the database, The engine then determines whether the incoming
metric value violates the configured threshold rule.

If a state transition occurs, two actions are performed:

- The `AlertState` record is updated to reflect the new condition
- A corresponding `AlertEvent` is created to record the transition

State transitions occur in two situations:

- Trigger: `ok → warning`

    The metric value has crossed the configured threshold

- Recovery: `warning → ok`

    The metric value has returned to a healthy range

Alert events are generated only when a state transition occurs, preventing repeated
alerts while a metric remains in the same condition.

When a trigger or recovery occurs, the event is logged and stored in the alert history.

**Note:** The `AlertEngine` evaluation logic verify required consecutive checks before
a state change.

## 7. Looping and Scheduling

Looping behavior depends on the execution mode:

In **CLI interface**, the main loop is implemented in `engine.py`, where the monitoring
cycle runs continuously.

In the **web-based dashboard**, the looping logic is coordinated through FastAPI in `app.py` (backend)
and periodic updates handled by `app.js` on the frontend.