import socket
import logging
import uvicorn
import json
from pathlib import Path
from yaml import safe_load
from argparse import Namespace
from sqlalchemy.exc import OperationalError
from woninet.core.engine import NetworkMonitorCore
from woninet.utilities.arguments import args
from woninet.utilities.logger import get_core_logger, TRACE_LEVEL
from woninet.utilities.create_configuration import create_config_json

# Global Variables
LOGGING_YAML_PATH = Path(__file__).parent / "logging.yaml"
REMOTE_PROBE_IP = "8.8.8.8"
monitor = None


def detect_local_ip(logger: logging.Logger) -> str:
    """
    Determine the local IP address by opening a dummy UDP connection
    to `8.8.8.8:80`.

    Args:
        logger (Logger): Logger used for recording logs.

    Returns:
        str: IP address of device.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            logger.trace(f"Sending a dummy UDP request to {REMOTE_PROBE_IP}:80")
            s.connect((REMOTE_PROBE_IP, 80))
            return s.getsockname()[0]
    except OSError:
        logger.error("Network is unreachable. Quitting.")
        raise SystemExit(1)
    except Exception as e:
        logger.error(f"Local IP detection failed: {e}")
        raise SystemExit(1)


def load_logging_yaml(log_output: str | None) -> dict:
    """
    Load logging YAML configuration and adjust file handler if needed.

    Args:
        log_output (str): The file path to save logs.

    Returns:
        dict: Logging configuration for uvicorn.
    """
    with open(LOGGING_YAML_PATH) as file:
        config = safe_load(file)

    if log_output:
        config["handlers"]["file"]["filename"] = log_output
    else:
        config["handlers"].pop("file", None)

        for logger in config.get("loggers", {}).values():
            handlers = logger.get("handlers", [])
            if "file" in handlers:
                handlers.remove("file")

    return config


def load_config_json(config_json_path: str) -> dict:
    """
    Load the application's JSON configuration file.

    If the configuration file does not exist, create a default one and
    load it again.

    Args:
        config_json_path (str): Path to the configuration JSON file.

    Returns:
        dict: Parsed configuration data.
    """
    try:
        with open(config_json_path) as file:
            config = json.load(file)
        return config
    except FileNotFoundError:
        create_config_json(config_json_path)

        with open(config_json_path) as file:
            config = json.load(file)
        return config


def configure_logger(arguments: Namespace) -> logging.Logger:
    """
    Initialize the core logger and adjust verbosity.
    """
    log_output = arguments.logs
    use_color = arguments.color != "false"

    core_logger = get_core_logger(log_output, use_color)

    if arguments.verbose == 1:
        core_logger.setLevel(logging.DEBUG)
    elif arguments.verbose >= 2:
        core_logger.setLevel(TRACE_LEVEL)

    if not arguments.cli:
        core_logger.setLevel(logging.ERROR)

    return core_logger


def create_monitor(
    local_ip: str,
    target_ip: str,
    database_path: str,
    arp_noise_limit: float,
    max_thread_workers: int,
    logger: logging.Logger,
    alert_rules: dict,
) -> NetworkMonitorCore:
    """
    Create an instance of NetworkMonitorCore.

    Args:
        local_ip (str): IP address of device.
        target_ip (str): A single or range of user-provided IP addresses to scan.
        database_path (str): Path to SQLite database.
        arp_noise_limit (float): Threshold above which ARP fluctuations are treated as noise.
        max_thread_workers (int): The concurrency limit for the
            `ThreadPoolExecutor` handling ICMP probes
        logger (Logger): Logger used for recording logs
        alert_rules (dict): alert_rules loaded from config.json.

    Returns:
        NetworkMonitorCore: Instance of NetworkMonitorCore.
    """
    global monitor
    if monitor is None:
        logger.debug(f"ARP noise limit set to {arp_noise_limit}")
        logger.trace(f"Using {database_path} as SQLite database.")
        logger.trace(f"Max thread workers for scanning set to {max_thread_workers}.")
        monitor = NetworkMonitorCore(
            local_ip=local_ip,
            target_ip=target_ip,
            arp_noise_limit=arp_noise_limit,
            database_path=database_path,
            max_thread_workers=max_thread_workers,
            alert_rules=alert_rules,
        )
    return monitor


def get_monitor() -> NetworkMonitorCore:
    """
    Returns the instance of NetworkMonitorCore for easier access in both CLI mode
    and web dashboard.
    """
    global monitor
    return monitor


def run_server(ip: str, port: int, log_yaml: dict) -> None:
    """
    Initialize and run the uvicorn ASGI server.

    Args:
        ip (str): Host used for running the server.
        port (int): Port number to serve the host.
        log_yaml (dict): Logging configuration for uvicorn.
    """
    from woninet.server.app import app

    config = uvicorn.Config(app, host=ip, port=port, log_config=log_yaml)
    server = uvicorn.Server(config)
    app.state.uvicorn_server = server
    server.run()


def main() -> None:
    """
    Entry point for woninet. Launch either the web dashboard or the CLI
    monitor based on command-line arguments.
    """
    global monitor

    arguments = args()

    if arguments.version:
        from woninet.__init__ import __version__

        print(__version__)
        return

    config_json_path = arguments.config
    configuration = load_config_json(config_json_path)

    target_ip = configuration["target_ip_list"]
    port = arguments.port

    core_logger = configure_logger(arguments=arguments)
    log_yaml = load_logging_yaml(log_output=arguments.logs)

    local_ip = detect_local_ip(logger=core_logger)

    try:
        if hasattr(arguments, "func"):
            core_logger.setLevel(logging.ERROR)

        monitor = create_monitor(
            local_ip=local_ip,
            target_ip=target_ip,
            database_path=configuration["database"],
            arp_noise_limit=configuration["monitoring"]["arp_noise_limit"],
            max_thread_workers=configuration["monitoring"]["max_workers"],
            logger=core_logger,
            alert_rules=configuration["alert_rules"],
        )

        if hasattr(arguments, "func"):
            arguments.monitor = monitor
            arguments.func(arguments)
            return

        if arguments.cli:
            monitor.start()
            monitor.wait()
        else:
            run_server(ip=local_ip, port=port, log_yaml=log_yaml)
    except KeyboardInterrupt:
        core_logger.info("Keyboard interrupted. Wait for shut down...")
    except ValueError as e:
        core_logger.error(f"{e} Quitting.")
    except FileNotFoundError:
        core_logger.error("Can not find the config.json file. Quitting.")
    except OperationalError as e:
        core_logger.error(e)
    finally:
        if hasattr(monitor, "stop"):
            monitor.stop()
