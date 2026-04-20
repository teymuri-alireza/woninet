import socket
import logging
import uvicorn
from .core.engine import NetworkMonitorCore
from .utilities.arguments import args
from .utilities.logger import logger_function, TRACE_LEVEL

# Global Variables
REMOTE_PROBE_IP = "8.8.8.8"
PORT = 8080

# Get Logger Configuration
rootLogger = logger_function()

argument = args()

# The --version Argument
if argument.version:
    from .utilities.version import show_version
    print(show_version())
    exit(0)

# Set Verbosity
if argument.verbose == 0:
    pass
elif argument.verbose == 1:
    rootLogger.setLevel(logging.DEBUG)
else:
    rootLogger.setLevel(TRACE_LEVEL)

# Set ERROR level for server mode to suppress CLI-related logs
if argument.serve:
        rootLogger.setLevel(logging.ERROR)

# Fetch The Local IP Address
try:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        rootLogger.trace(f"Sending a dummy UDP request to {REMOTE_PROBE_IP}:80")
        s.connect((REMOTE_PROBE_IP, 80))
        local_ip = s.getsockname()[0]
except OSError:
    rootLogger.error("Network is unreachable. Quitting.")
    exit(1)
except Exception as e:
    rootLogger.error(f"Error at socket connection in main.py: {e}")
    exit(1)


def get_monitor() -> NetworkMonitorCore:
    """
    Returns an instance of NetworkMonitoreCore for easier access in both CLI mode
    and server dashboard.
    """
    monitor = NetworkMonitorCore(ip_addr=local_ip)
    return monitor

def main():
    """
    The main entry point of woninet; Which decides to either call server
    dashboard or the CLI interface.
    """
    if argument.serve:
        from woninet.server.app import app
        uvicorn.run(app, host=local_ip, port=PORT)
    else:
        try:
            monitor = get_monitor()
            while True:
                monitor.start()
                monitor.clear_history()
        except Exception as e:
            rootLogger.error(f"Error in main.py: {e}")
            exit(1)