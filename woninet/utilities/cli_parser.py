from woninet.main import NetworkMonitorCore


def list_devices(args):
    """
    Prints list of recorded devices information from the database to stdout.
    Following entries are shown:
    1. Device IP address.
    2. Device MAC address.
    3. Device last seen timestamp.
    """
    monitor: NetworkMonitorCore = args.monitor
    devices = monitor.get_device_history()
    if len(devices) == 0:
        print("No recorded device was found.")
    else:
        for device in devices:
            row = f"Device {device.ip}: MAC={device.mac}, Last seen={device.last_seen}"
            print(row)
    exit(0)


def show_device_info(args):
    """
    Prints information for a given IP address. Following entries are shown:
    1. Device IP address.
    2. Device MAC address.
    3. Device last captured latency.
    4. Device last seen timestamp.
    5. Last alert state of device.
    6. Last 10 alert events of device.
    """
    monitor: NetworkMonitorCore = args.monitor
    device, device_state, recent_device_alert_events = monitor.get_device_info(args.ip)
    if device is None:
        print(f"Device {args.ip} was not found.")
    else:
        latency = device.latency
        if latency == 0:
            latency = "OFFLINE"
        print(
            f"Found device {device.ip}: MAC={device.mac}, Last latency: {latency}, Last seen={device.last_seen}"
        )
        for metric, state in device_state.items():
            print(f"Current alert state for {metric}: state={state}")
        print("Recent alert events:")
        for event in recent_device_alert_events:
            content = f"ID: {event.id} - Metric: {event.metric},\t Value={event.value},"
            content += (
                f"\t Event type={event.event_type},\t Timestamp={event.timestamp}"
            )
            print(content)
    exit(0)
