import json
import ping3
import nmap
import datetime
import os
from concurrent.futures import ThreadPoolExecutor
from utilities.logger import logger_function

# get logger configuration
rootLogger = logger_function()

# global variables
SCRIPT_PATH = "/usr/local/lib/pymonitor"
SCAN_FILES = f"{SCRIPT_PATH}/scan-files"

try:
    os.mkdir(f"{SCAN_FILES}/")
except FileExistsError:
    pass
except PermissionError:
    # postpone error to load -h and -V without root access
    pass

def scan_logic(ipAddr: str, nmap_command: list) -> int:
    """
    The logic for scanning local network.

    This function calles generate_ip for generating 255 IP addreses (from x.x.x.1 to x.x.x.254),
    then calls the ping_function to check which IP address is up. Then returns the result to server (main.py).

    Parameters:
        ipAddr (str) : Private IP of the device.

        nmap_command (list | None) : The nmap command to perform against found IP addresses.

    Returns:
        int : Exit code of the function (0 for success, -1 for failure).
    """
    if ipAddr.strip == "":
        rootLogger.error("IP address is empty. Quitting scan_logic function.")
        return -1
    exit_code = generate_ip(ipAddr)
    if exit_code == 0:
        exit_code = ping_function(src_ip=ipAddr)

        if nmap_command is not None:
            nmap_scan(nmap_command=nmap_command)

        if exit_code == 0:
            return 0
    return -1

def generate_ip(ipAddr: str) -> int:
    """
    Generates 255 IPs on a local network. (from x.x.x.1 to x.x.x.254).

    Parameters:
        ipAddr (str) : Private IP of the device.

    Returns:
        int : Exit code of the function (0 for success, -1 for failure).
    """
    try:
        ip_seperate = ipAddr.split(".")
        with open(f"{SCAN_FILES}/ip_list.txt", "w") as file:
            for i in range(1,255):
                file.write(f"{ip_seperate[0]}.{ip_seperate[1]}.{ip_seperate[2]}.{i}\n")
        rootLogger.debug(f"254 IP address generated based on {ip_seperate[0]}.{ip_seperate[1]}.{ip_seperate[2]}.x")
        return 0
    
    except PermissionError:
        rootLogger.error("Are you root?")
        exit(1)
    
    except Exception as e:
        rootLogger.error(f"Error at generate_ip function in scan.py file: {e}")
        return -1

def update_history() -> None:
    """
    Saves the result of ping scan into history.txt file with a date format similar to
    the logger format.
    """
    try:
        # preparing the date format
        time_now = datetime.datetime.now()
        month_list = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        day = time_now.day
        month = month_list[time_now.month - 1]
        year = time_now.year
        hour = time_now.hour
        minute = time_now.minute
        second = time_now.second
        date_format = f"[{year}/{month}/{day} {hour}:{minute}:{second}]"
        # writing into file
        with open(f"{SCAN_FILES}/history.txt", "a") as history:
            with open(f"{SCAN_FILES}/ping_result.txt", "r") as ping_result:
                for line in ping_result:
                    history.write(f"{date_format} {line.strip()}\n")
        # root logger moved to main.py to handle monitor mode
    
    except PermissionError:
        rootLogger.error("Are you root?")
        exit(1)

    except Exception as e:
        rootLogger.error(f"Error at update_history function in scan.py file: {e}")

def ping_function(src_ip: str) -> int:
    """
    Sends an ICMP ping request, using python ping3 module
    to every IP in ip_list.txt file,
    then stores the accepted responses in ping_result.txt.

    This function skips scanning IP addresses in settings.json.

    Parameters:
        src_ip (str) : Private IP of the device

    Returns:
        int : Exit code of the functions (0 for success, -1 for failure).
    """
    try:
        with open(f"{SCRIPT_PATH}/settings.json", "r") as file:
            settings = json.load(file)

        with open(f"{SCAN_FILES}/ping_result.txt", "w") as ping_result:
            with open(f"{SCAN_FILES}/ip_list.txt", "r") as ip_list_file:
                def ping_main_logic(line: str) -> None:
                        """
                        This function is used in ThreadPoolExecutor for faster scans.

                        The response time in is shortened and converts to millisecond.

                        Parameters:
                            line (str) : Every IP of the private network, gathered from generate_ip function.
                        """
                        response = ping3.ping(src_addr=src_ip,dest_addr=line.strip(), timeout=1, ttl=64)
                        if response is not None and response is not False:
                            rootLogger.debug(f"{line.strip()} is up.")
                            response_split = str(response)[4:8]
                            value = response_split[0] + "." + response_split[1:] + " ms"
                            ping_result.write(f"{line.strip()}: {value}\n")
                
                with ThreadPoolExecutor(max_workers=20) as executor:
                    for line in ip_list_file:
                        if line.strip() in settings["known_ip"]:
                            # skip the scan if IP exist in the settings.json
                            continue
                        
                        executor.submit(ping_main_logic, line)
        update_history()
        return 0
    
    except PermissionError:
        rootLogger.error("Are you root?")
        exit(1)

    except FileNotFoundError as e:
        rootLogger.error(f"Error at ping_function function in scan.py file: {e}")
        return -1

def nmap_scan(nmap_command: str):
    """
    Performs a nmap scan against found IP addresses.
    
    Parameters:
        nmap_command (str) : The filename to be used for output.
    """
    # nmap command is not None here because it was handled in the scan_logic function.
    try:
        output = {}
        port_scanner = nmap.PortScanner()
        rootLogger.debug("Initializing nmap port scanner.")
        with open(f"{SCAN_FILES}/ping_result.txt", "r") as ping_result:
            for ip in ping_result:
                # prettify the ip address
                ip = ip.split(":")[0]
                ip = ip.strip()
                rootLogger.debug(f"Nmap scan for {ip}...")
                # join options
                nmap_args = " ".join(nmap_command)
                output[ip] = port_scanner.scan(hosts=ip, arguments=nmap_args, ports="1-1000" ,sudo=True)
        
        # saving results
        filename = "output.json"
        with open(filename, "w") as results:
            rootLogger.info(f"Saving nmap scan results to {filename}")
            json.dump(output, results, indent=4)

    except PermissionError:
        rootLogger.error("You need root access. Quitting.")
        exit(1)

    except Exception as e:
        rootLogger.error(f"Error at nmap_scan function in scan.py: {e}")