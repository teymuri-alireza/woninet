#!/usr/bin/python3

import json
import ping3
import datetime
import os
from utilities.logger import logger_function
# get logger configuration
rootLogger = logger_function()
# global variables
SCRIPT_PATH = "/usr/local/lib/.pymonitor"
SCAN_FILES = f"{SCRIPT_PATH}/scan-files"

try:
    os.mkdir(f"{SCAN_FILES}/")
except FileExistsError:
    pass

def scan_logic(ipAddr: str) -> int:
    """
    The logic for scanning local network.

    This function calles generate_ip for generating 255 IP addreses (from x.x.x.1 to x.x.x.254),
    then calls the ping_function to check which IP address is up. Then returns the result to server (main.py).

    Parameters:
        ipAddr (str) : Private IP of the device.

    Returns:
        int : Exit code of the function (0 for success, -1 for failure).
    """
    if ipAddr.strip == "":
        rootLogger.error("IP address is empty. Quitting scan_logic function.")
        return -1
    exit_code = generate_ip(ipAddr)
    if exit_code == 0:
        exit_code = ping_function()
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
        return 0
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
        rootLogger.info(f"History updated at {SCAN_FILES}/history.txt")
    except Exception as e:
        rootLogger.error(f"Error at update_history function in scan.py file: {e}")

def ping_function() -> int:
    """
    Sends an ICMP ping request to every IP in ip_list.txt file,
    then stores the accepted responses in ping_result.txt.

    The response time in ping_result.txt is shortened and converts to millisecond.

    This function skips scanning IP addresses in settings.json.

    This functions uses python ping3 module.

    Returns:
        int : Exit code of the functions (0 for success, -1 for failure).
    """
    try:
        with open(f"{SCRIPT_PATH}/settings.json", "r") as file:
            settings = json.load(file)

        with open(f"{SCAN_FILES}/ping_result.txt", "w") as ping_result:
            with open(f"{SCAN_FILES}/ip_list.txt", "r") as ip_list_file:
                for line in ip_list_file:

                    if line.strip() in settings["known_ip"]:
                        # skip the scan if IP exist in the settings.json
                        continue
                    
                    response = ping3.ping(src_addr="192.168.1.33",dest_addr=line.strip(), timeout=1, ttl=64)
                    if response is not None and response is not False:
                        response_split = str(response)[4:8]
                        value = response_split[0] + "." + response_split[1:] + " ms"
                        ping_result.write(f"{line.strip()}: {value}\n")
        update_history()
        return 0
    except FileNotFoundError as e:
        rootLogger.error(f"Error at ping_function function in scan.py file: {e}")
        return -1