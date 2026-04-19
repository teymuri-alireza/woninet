def get_monitor_gracefully():
    """
    Calls get_monitor() and returns the intance of NetworkMonitorCore class
    to prevent circular import error.
    """
    from woninet.main import get_monitor
    monitor = get_monitor()
    return monitor


def get_network_stats():
    return {
        "stat": "ok"
    }