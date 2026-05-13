from woninet.main import NetworkMonitorCore


def list_devices(args):
    monitor: NetworkMonitorCore = args.monitor
    for device in monitor.get_device_history():
        row = f"Device {device.ip}: MAC={device.mac}, Last seen={device.last_seen}"
        print(row)
    exit(0)


def show_device_info(args):
    monitor: NetworkMonitorCore = args.monitor
    device, device_state, recent_device_alert_events = monitor.get_device_info(args.ip)
    if device is None:
        print(f"Device {args.ip} was not found.")
    else:
        print(
            f"Found device {device.ip}: MAC={device.mac}, Last seen={device.last_seen}"
        )
        metric, state = device_state
        print(f"Current alert state for {metric}: state={state}")
        print("Recent alert events:")
        for event in recent_device_alert_events:
            content = f"ID: {event.id} - Metric: {event.metric},\t Value={event.value},"
            content += (
                f"\t Event type={event.event_type},\t Timestamp={event.timestamp}"
            )
            print(content)
    exit(0)
