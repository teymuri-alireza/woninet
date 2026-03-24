import argparse

def args(set_socket, set_port):
    """
    The argument handler.

    check `pymonitor -h` for more info.
    """
    description = """
A local network inspecter and monitoring system written in python3.
This tool get your local private IP, then generate 254 IP addresses 
to scan."""

    epilog = """Note:
  -p only make sense if used with --serve.
  -c prompts user for configuration settings then closes the proram.
  To change the socket value permanently, use --config ( -c ).
  -n and -m only work in cli mode.

Examples:
  sudo pymonitor
  sudo pymonitor -s 8.8.8.8
  sudo pymonitor -p 8000 --serve
  sudo pymonitor -v -n
  sudo pymonitor -v -n \"-A -sX\""""

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        prog="pymonitor",
        epilog=epilog
    )

    parser.add_argument(
        "-m", "--monitor",
        action="store_true",
        help="Keeps scanning until KeyboardInterrupt. (Only works in cli mode)"
    )

    parser.add_argument(
        "-n", "--nmap",
        type=str,
        nargs='*',
        help="Performs a nmap scan against found IP addresses."
    )

    parser.add_argument(
        "-s", "--socket",
        type=set_socket,
        help="Set socket for private IP determination; for the current scan only. (default: 8.8.8.8)"
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
        "-v", "--verbose",
        action="store_true",
        help="Talks more."
    )
    
    parser.add_argument(
        "-c", "--config",
        action="store_true",
        help="Modify the configuration file and quit."
    )

    parser.add_argument(
        "-V", "--version",
        action="store_true",
        help="Prints the version and quit."
    )

    return parser.parse_args()