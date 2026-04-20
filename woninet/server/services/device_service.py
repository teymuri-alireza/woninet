def get_monitor_gracefully():
    """
    Calls get_monitor() and returns the intance of NetworkMonitorCore class
    to prevent circular import error.
    """
    from woninet.main import get_monitor
    monitor = get_monitor()
    return monitor

def get_devices():
    monitor = get_monitor_gracefully()
    monitor.start()
    return {
        "devices": monitor.get_devices()
    }