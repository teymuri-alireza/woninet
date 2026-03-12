import ping3
from logger import logger_function
# get logger configuration
rootLogger = logger_function()
# setting scan files path
SCAN_FILES = "scan-files"

def scanLogic(ipAddr: str):
    """
    The logic for scanning local network.

    This function calles generateIP for generating 255 IP addreses, then calls
    pingFunction to check which IP address is up. Then returns the result to server
    to be sent to JavaScript in the front-end.

    Parameters:
        ipAddr (str) : private IP of the device
    """
    if ipAddr.strip == "":
        return -1
    exit_code = generateIP(ipAddr)
    if exit_code == 0:
        pass

def generateIP(ipAddr: str) -> int:
    """
    Generates 255 IPs on a local network

    Parameters:
        ipAddr (str) : private IP of the device

    Returns:
        int : exit code of the function (0 for success, -1 for failure)
    """
    try:
        ip_seperate = ipAddr.split(".")
        with open(f"{SCAN_FILES}/ip_list.txt", "w") as file:
            for i in range(1,255):
                file.write(f"{ip_seperate[0]}.{ip_seperate[1]}.{ip_seperate[2]}.{i}")
        return 0
    except Exception as e:
        rootLogger.error(f"Error at generateIP function in scan.py file: {e}")
        return -1