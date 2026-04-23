# Core Logic

This section explains the full sequence of operations *woninet* performs to scan and monitor the local network.

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
- Initial settings (intervals, alert rules, logging config)
- The full state containers (devices, history, alerts)

The core is responsible for orchestrating:

- Subnet enumeration
- Host detection
- Metric collection
- Data storage
- Alert evaluation
- Logging

It is the central controller of the system.

## 3. Subnet Enumeration (/24 Range)

*woninet* uses the SubnetEnumerator class to generate a dictionary of candidate devices within the local `/24` subnet.

For a source IP such as:

```text
192.168.1.23
```

It builds the full CIDR block:

```text
192.168.1.1 - 192.168.1.254
```

This step doesn't determine if devices exist or respond — it only constructs the list of potential addresses.

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
reachable = False
```

No ICMP probing is attempted for non-existing hosts.

### Stage B — ICMP Ping (if ARP succeeded)

If ARP confirms existence, *woninet* sends an ICMP ping using `icmplib`.

Latency is interpreted carefully:

- latency < 300 ms → valid response
- latency ≥ 300 ms → considered "ARP delay noise," treated as unreachable
- `None` → no ICMP reply

Device fields updated:

- exists
- reachable
- latency
-last_seen (only updated when reachable)

This filters out false positives common on Wi‑Fi networks, where ARP proxying or delayed ARP replies cause misleading high ping times.

## 5. History Storage

The StorageEngine now maintains two separate in‑memory histories:

- Device history (device discoveries and status updates)
- Metric history (latency and reachability measurements)

### Metric History

Each valid measurement (ARP-confirmed + reachability) is stored as a MetricRecord, containing:

- timestamp
- IP address
- Metric
- latency

### Device History

Each device-related update is stored as a Device class, containing:

- last_seen
- IP address
- Metrics
- Existence
- Reachability
- MAC address
- Latency

Both histories are currently stored in-memory, meaning they are cleared when the program exits.

## 6. Alert Engine Evaluation

After every monitoring cycle, all stored metrics are passed to the `AlertEngine`.

Each rule evaluates conditions such as:

- latency higher than a threshold
- device unreachable
- high jitter (future update)

If a rule is triggered, an alert event is logged.

## 7. Looping and Scheduling

Looping behavior depends on the execution mode.

For the **CLI interface**, the loop is implemented in `main.py`.

For the web-based dashboard, the looping logic is handled within the web service layer. (future update)
