"""
This is the main entry point of the script. Argumment handlers, configuration settings and CLI mode are
processed in this file. The server option, loggings, argument definitions and scan logic are written in other files.
For more info check out the documentation.md file
"""

import socket
import os
import datetime
from utilities.logger import logger_function

# get logger configuration
rootLogger = logger_function()

# global variables
SOCKET = "8.8.8.8"

# import utilities after checking settings to prevent unplanned PermissionError
from scan import scan_logic
from utilities.arguments import args
from utilities.validate_ip import validate_ip

# calling argument handler
argument = args()

# handle the --version argument
if argument.version:
    from utilities.version import show_version
    print(show_version())
    exit(0)

# check verbosity
if argument.verbose:
    from logging import DEBUG
    rootLogger.setLevel(DEBUG)

# get the local IP address
try:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect((SOCKET, 80))
        local_IP = s.getsockname()[0]
except OSError:
    rootLogger.error("Network is unreachable. Quitting.")
    exit(1)
except Exception as e:
    rootLogger.error(f"Error at socket connection in main.py: {e}")
    exit(1)

# the CLI mode
rootLogger.debug("Entering CLI mode scanner.")
print(f"Your private IP: {local_IP}")

menu = """1. Scan the network
0. Exit
Choose: """

# logging monitor mode
if MONITOR_MODE:
    rootLogger.info("Monitor mode is on.")

while True:
    try:
        if MONITOR_MODE:
            choice = 1
        else:
            choice = input(menu)

        if int(choice) == 0:
            exit(0)
        
        elif int(choice) == 1:
            print("Starting scan...")
            scan_start_time = datetime.datetime.now()
            # check --nmap value
            if argument.nmap == []:
                # set a default value
                nmap_command = ["-sS", "-O"]
            elif argument.nmap == None:
                nmap_command = None
            else:
                nmap_command = argument.nmap
            
            result = scan_logic(local_IP, nmap_command=nmap_command)
            
            if result == -1:
                # The error will be printed from the scan_logic function
                exit(1)
            
            elif result == 0:
                with open(f"{SCRIPT_PATH}/scan-files/ping_result.txt", "r") as file:
                    ping_result = file.read()
                    
                    # if no result was found
                    scan_finish_time = datetime.datetime.now()
                    if ping_result.strip() == "":
                        print("No result!")
                    else:
                        print("Scan finished.")
                        print(ping_result, end="")
                    
                    if not MONITOR_MODE:
                        # The monitor mode suppose to run scans one after another.
                        # printing time and logger in update_history after each turn is disturning
                        time_took = scan_finish_time - scan_start_time
                        rootLogger.debug(f"Time took: {str(time_took)[0:-4]}")
                        rootLogger.debug(f"History updated at {SCRIPT_PATH}/scan-files/history.txt")

                    print()
        
        else:
            print("Try again.")
    
    except ValueError:
        rootLogger.error("Input must be an integer.")
    
    except KeyboardInterrupt:
        rootLogger.info("Keyboard Interrupted. Wait for shutting down.")
        exit(130)
    
    except Exception as e:
        rootLogger.error(f"Error occured: {e}")
        exit(1)