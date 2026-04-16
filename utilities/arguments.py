import argparse

def args():
    """
    The argument handler.

    check `pymonitor -h` for more info.
    """
    description = """
A local network inspecter and monitoring system written in python3. This tool creates 254 IP addresses based on your local IP, then ping each of them and prints the found IP addresses."""

    epilog = ""

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        prog="pymonitor",
        epilog=epilog
    )

    # parser.add_argument(
    #     "--serve",
    #     action="store_true",
    #     help="Serve the server instead of CLI mode."
    # )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Talks more."
    )

    parser.add_argument(
        "-V", "--version",
        action="store_true",
        help="Prints the version and quit."
    )

    return parser.parse_args()