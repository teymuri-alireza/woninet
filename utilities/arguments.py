#!/usr/bin/python3

import argparse

def args(set_socket, set_port):
    """
    The argument handler.

    check `python3 main.py -h` for more info.
    """
    description = """
A local network inspecter and monitoring system written in python3.
This tool get your local private IP, then generate 254 IP addresses
to scan.

Examples:
    sudo python3 main.py
    sudo python3 main.py -s 8.8.8.8
    sudo python3 main.py -p 8000 --serve

Note: -p only make sense if used with --serve
Note: -c promts user for configuration then closes the proram"""

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "-s", "--socket",
        type=set_socket,
        help="Set socket for private IP determination. (default: 8.8.8.8)"
    )

    parser.add_argument(
        "--serve",
        action="store_true",
        help="Serve the server instead of CLI mode."
    )

    parser.add_argument(
        "-p", "--port",
        type=set_port,
        help="Set port for the server. (default: 8000)"
    )
    
    parser.add_argument(
        "-c", "--config",
        action="store_true",
        help="Modify the configuration file."
    )

    return parser.parse_args()