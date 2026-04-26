import argparse


def args():
    """
    The argument handler.

    check `woninet -h` for more info.
    """
    description = """
A local network monitoring system. It enumerates all candidate IP addresses in your /24 subnet and performs ARP + ICMP host detection to determine existence, reachability, and latency. Metrics are collected continuously and processed through an alert engine."""

    epilog = ""

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        prog="woninet",
        epilog=epilog,
    )

    parser.add_argument(
        "--serve",
        action="store_true",
        help="Starts the server for web-based dashboard.",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Output path for storing logs.",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Talks more. (Can be used multiple times)",
    )

    parser.add_argument(
        "-V", "--version", action="store_true", help="Prints the version and quit."
    )

    return parser.parse_args()
