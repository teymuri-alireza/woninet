import socket
import logging
from .core.engine import NetworkMonitorCore
from .utilities.arguments import args
from .utilities.logger import logger_function, TRACE_LEVEL

# Global Variables
SOCKET = "8.8.8.8"

# Get Logger Configuration
rootLogger = logger_function()

argument = args()

# The --version Argument
if argument.version:
    from utilities.version import show_version
    print(show_version())
    exit(0)

# Set Verbosity
if argument.verbose == 0:
    pass
elif argument.verbose == 1:
    rootLogger.setLevel(logging.DEBUG)
else:
    rootLogger.setLevel(TRACE_LEVEL)

# Fetch The Local IP Address
try:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        rootLogger.trace(f"Sending a dummy UDP request to {SOCKET}:80")
        s.connect((SOCKET, 80))
        local_ip = s.getsockname()[0]
except OSError:
    rootLogger.error("Network is unreachable. Quitting.")
    exit(1)
except Exception as e:
    rootLogger.error(f"Error at socket connection in main.py: {e}")
    exit(1)


def main():
    try:
        monitor = NetworkMonitorCore(ip_addr=local_ip)
        monitor.start()
    except KeyboardInterrupt:
        rootLogger.info("Keyboard Interrupted. Wait for shutting down.")
    except PermissionError:
        rootLogger.error("woninet requires sudo to scan.")
        exit(1)
    except Exception as e:
        rootLogger.error(f"Error occured: {e}")
        exit(1)