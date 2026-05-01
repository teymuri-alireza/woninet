def get_monitor_gracefully():
    """
    Call get_monitor() and return the intance of NetworkMonitorCore class
    to prevent circular import error.
    """
    from woninet.main import get_monitor

    monitor = get_monitor()
    return monitor


def get_network_stats():
    return {"stat": "ok"}
