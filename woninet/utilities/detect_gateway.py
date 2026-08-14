from logging import getLogger
import platform
import subprocess

core_logger = getLogger("core")


def get_default_gateway() -> str:
    """
    Return the system's default IPv4 gateway address.

    This function detects the current operating system and runs the appropriate
    command to determine the default gateway IP address for IPv4 traffic.

    Logic:
    - On Linux: runs `ip route show default` and parses the output, returning
      the token immediately following the "via" keyword.
    - On Windows: runs a PowerShell command to get the IPv4 default gateway
      (Get-NetIPConfiguration).IPv4DefaultGateway.NextHop and returns the
      first non-empty line of output.

    Returns:
        str: The default gateway IP as a string if found, otherwise None.

    Raises:
        NotImplementedError: if the current OS is not supported.
    """

    system = platform.system()

    if system == "Linux":
        result = subprocess.run(
            ["ip", "route", "show", "default"],
            capture_output=True,
            text=True,
            check=True,
        )

        fields = result.stdout.split()

        try:
            return fields[fields.index("via") + 1]
        except ValueError as e:
            core_logger.error(f"Error in get_default_gateway(): {e}")

    elif system == "Windows":
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "(Get-NetIPConfiguration).IPv4DefaultGateway.NextHop",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        gateways = [line.strip() for line in result.stdout.splitlines() if line.strip()]

        return gateways[0] if gateways else None

    else:
        raise NotImplementedError(f"Other operating systems will be implemented later. Current system: {system}")
