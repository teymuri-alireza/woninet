import socket
import logging
import uvicorn
from pathlib import Path
from yaml import safe_load
from woninet.core.engine import NetworkMonitorCore
from woninet.utilities.arguments import args
from woninet.utilities.logger import logger_function, TRACE_LEVEL

# Global Variables
LOGGING_YAML_PATH = Path(__file__).parent / "logging.yaml"
REMOTE_PROBE_IP = "8.8.8.8"
PORT = 8080

# Load YAML
with open(LOGGING_YAML_PATH) as file:
    LOGGING_YAML = safe_load(file)

# Get Logger Configuration
rootLogger = logger_function()

argument = args()

# The --version Argument
if argument.version:
    from woninet.__init__ import __version__

    print(__version__)
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

monitor = None


def get_monitor() -> NetworkMonitorCore:
    """
    Return an instance of NetworkMonitoreCore for easier access in both CLI mode
    and web dashboard.
    """
    global monitor
    if monitor is None:
        monitor = NetworkMonitorCore(ip_addr=local_ip)
    return monitor


def main():
    """
    Entry point for woninet. Launch either the web dashboard or the CLI
    monitor based on command-line arguments.
    """
    if argument.serve:
        from woninet.server.app import app

        uvicorn.run(app, host=local_ip, port=PORT, log_config=LOGGING_YAML)
    else:
        try:
            monitor = get_monitor()
            monitor.start()
            monitor.wait()
        except KeyboardInterrupt:
            rootLogger.info("Keyboard interrupted. Wait for shut down...")
        finally:
            monitor.stop()
