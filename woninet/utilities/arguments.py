import argparse
from woninet.utilities.cli_parser import list_devices, show_device_info, report_stats


def args() -> argparse.Namespace:
    """
    The argument handler.

    check `woninet -h` for more info.
    """
    description = """
A local network monitoring system. It enumerates all candidate IP addresses in your /24 subnet
and performs ARP + ICMP host detection to determine existence, reachability, and latency. Metrics
are collected continuously and processed through an alert engine."""

    epilog = ""

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        prog="woninet",
        epilog=epilog,
    )

    subparsers = parser.add_subparsers(dest="command")

    device_parser = subparsers.add_parser(
        "device", help="Fetch Device informations from the database."
    )
    device_subparsers = device_parser.add_subparsers(dest="action", required=True)

    device_list = device_subparsers.add_parser(
        "list", description="List all devices.", help="List all devices."
    )
    device_list.set_defaults(func=list_devices)

    device_show = device_subparsers.add_parser(
        "show", description="Show device info for a given IP.", help="Show device info."
    )
    device_show.add_argument("ip", help="Device IP address")
    device_show.set_defaults(func=show_device_info)

    stats_parser = subparsers.add_parser(
        "stats", help="Output a JSON report for the woninet statistics."
    )

    stats_parser.add_argument(
        "--output",
        default="stats.json",
        help="Output path for the JSON report for the woninet statistics (default: %(default)s).",
    )
    stats_parser.set_defaults(func=report_stats)

    parser.add_argument(
        "--cli",
        action="store_true",
        help="Run woninet in CLI mode.",
    )

    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8080,
        help="Port number to serve the web dashboard (defaut: %(default)s).",
    )

    parser.add_argument(
        "--logs",
        type=str,
        help="Output path for storing logs.",
    )

    parser.add_argument(
        "--color",
        type=str,
        choices=["true", "false"],
        default="true",
        help="Whether to enable colored console log output (default: %(default)s)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (repeat for more detail)",
    )

    parser.add_argument(
        "-V", "--version", action="store_true", help="Prints the version and quit."
    )

    return parser.parse_args()
