import ping3
from logger import logger_function
# get logger configuration
rootLogger = logger_function()
# setting scan files path
SCAN_FILES = "scan-files"

def scanLogic(ipAddr: str) -> int:
    """
    The logic for scanning local network.

    This function calles generateIP for generating 255 IP addreses (from x.x.x.1 to x.x.x.254),
    then calls the pingFunction to check which IP address is up. Then returns the result to server (main.py).

    Parameters:
        ipAddr (str) : private IP of the device.

    Returns:
        int : exit code of the function (0 for success, -1 for failure).
    """
    if ipAddr.strip == "":
        rootLogger.error("IP address is empty. Quitting scanLogic function.")
        return -1
    exit_code = generateIP(ipAddr)
    if exit_code == 0:
        exit_code = pingFunction()
        if exit_code == 0:
            return 0
    return -1

def generateIP(ipAddr: str) -> int:
    """
    Generates 255 IPs on a local network. (from x.x.x.1 to x.x.x.254).

    Parameters:
        ipAddr (str) : private IP of the device.

    Returns:
        int : exit code of the function (0 for success, -1 for failure).
    """
    try:
        ip_seperate = ipAddr.split(".")
        with open(f"{SCAN_FILES}/ip_list.txt", "w") as file:
            for i in range(1,255):
                file.write(f"{ip_seperate[0]}.{ip_seperate[1]}.{ip_seperate[2]}.{i}\n")
        return 0
    except Exception as e:
        rootLogger.error(f"Error at generateIP function in scan.py file: {e}")
        return -1

def pingFunction() -> int:
    """
    Sends an ICMP ping request to every IP in ip_list.txt file,
    then stores the accepted responses in ping_result.txt.

    The response time in ping_result.txt is shortened and converts to millisecond.

    This functions uses python ping3 module.

    Returns:
        int : exit code of the functions (0 for success, -1 for failure)
    """
    try:
        with open(f"{SCAN_FILES}/ping_result.txt", "w") as ping_result:
            with open(f"{SCAN_FILES}/ip_list.txt", "r") as ip_list_file:
                for line in ip_list_file:
                    response = ping3.ping(src_addr="192.168.1.33",dest_addr=line.strip(), timeout=1, ttl=64)
                    if response is not None and response is not False:
                        response_split = str(response)[4:8]
                        value = response_split[0] + "." + response_split[1:] + " ms"
                        ping_result.write(f"{line.strip()}: {value}\n")
        return 0
    except FileNotFoundError as e:
        rootLogger.error(f"Error at pingFunction function in scan.py file: {e}")
        return -1