"""
This is the main entry point of the script. Argumment handlers, configuration settings and CLI mode are
processed in this file. The server option, loggings, argument definitions and scan logic are written in other files.
For more info check out the documentation.md file
"""

import socket
import json
import os
import datetime
from utilities.logger import logger_function

# get logger configuration
rootLogger = logger_function()

# global variables
PORT = 8000
SCRIPT_PATH = "/usr/local/lib/pymonitor"

# check if settings.json exist
try:
    with open(f"{SCRIPT_PATH}/settings.json", "r") as file:
        pass
except FileNotFoundError:
    try:
        # make sure the directory exist
        try:
            os.mkdir(SCRIPT_PATH)
        except:
            pass
        
        # The base of the settings
        settings_structure = {
            "known_ip": [],
            "socket": "8.8.8.8"
        }
        with open(f"{SCRIPT_PATH}/settings.json", "w") as file:
            json.dump(settings_structure, file, indent=4)
            rootLogger.info(f"Creating settings at {SCRIPT_PATH}/settings.json")
    
    except PermissionError:
        # postpone error to load -h and -V without root access
        pass

# import utilities after checking settings to prevent unplanned PermissionError
from scan import scan_logic
from utilities.arguments import args
from utilities.validate_ip import validate_ip

try:
    # fetch socket from the settings
    with open(f"{SCRIPT_PATH}/settings.json", "r") as file:
        settings = json.load(file)
    SOCKET = settings["socket"]

except FileNotFoundError:
    # postpone error to load -h and -V without root access
    pass

except PermissionError:
    # postpone error to load -h and -V without root access
    pass

# functions for handling arguments
def set_socket(socket: str) -> None:
    """
    Sets a new value for socket, to get private IP.
    """
    if socket:
        global SOCKET
        SOCKET = socket

def set_port(port: int) -> None:
    """
    Sets a new vlaue for port, to serve the server.
    """
    if port:
        if port < 1 or port > 65535:
            rootLogger.error("PORT must be between 1 and 65535.")
            exit(1)
        global PORT
        PORT = int(port)

# calling argument handler
argument = args(set_socket=set_socket, set_port=set_port)

# handle the --version argument
if argument.version:
    from utilities.version import show_version
    print(show_version())
    exit(0)

# check verbosity
if argument.verbose:
    from logging import DEBUG
    rootLogger.setLevel(DEBUG)

# check monitor mode
MONITOR_MODE = False
if argument.monitor:
    MONITOR_MODE = True

try:
    # load settings
    with open(f"{SCRIPT_PATH}/settings.json", "r") as file:
        settings = json.load(file)

except FileNotFoundError:
    rootLogger.error("It seems like it's your first time running pymonitor. Run with 'sudo' to create settings.json.")
    exit(1)

except PermissionError:
    rootLogger.error("Are you root?")
    exit(1)

# enter configuration settings
if argument.config:
    rootLogger.debug("Entering configuration settings.")
    
    # ask for user's input
    menu = """1. Manage known IP list: Only unknown IP addresses will be shown in the ping result.
2. Change socket value permanently (for private IP determination)
9. Show current settings.
0. exit
choose: """
    try:
        choice = int(input(menu))

        if choice == 0:
            exit(0)
    
        elif choice == 1:
            print("Known IP settings:")
            print("Help: 1. seperate IP addresses with comma ( , )")
            print("      2. re-entrying an IP address will remove it.")
            ip_input = input("\tEnter your IP address: ")
            
            seperate_input = ip_input.split(",")
            for ip in seperate_input:
                ip = ip.strip()
                if ip == "":
                    continue

                # remove IP address, if they exist
                if ip in settings["known_ip"]:
                    settings["known_ip"].remove(ip)
                    rootLogger.info(f"Removing {ip} from known ip list.")
                else:
                    # validation and adding
                    if validate_ip(ip):
                        settings["known_ip"].append(ip)
                        rootLogger.info(f"Adding {ip} to known ip list.")
                    else:
                        # The error will be printed from the validate_ip function
                        print("Value(s) are not saved.")
                        exit(1)

            # sorting values
            settings["known_ip"].sort()

        elif choice == 2:
            print("Socket settings:")
            print("\tCurrent value: " + settings["socket"])
            new_socket = input("\tNew value: (0 to quit) ")
            
            if new_socket == "0":
                exit(0)
            
            settings["socket"] = new_socket
            rootLogger.info(f"Changing socket value to {new_socket}")

        elif choice == 9:
            rootLogger.debug("Requested displaying settings.")
            print("Known IP list: ", end="")
            if settings["known_ip"] == []:
                print("-")
            else:
                for ip in settings["known_ip"]:
                    print(ip, end=" - ")
                
                print() # to increase readability
            
            print(f"Socket value: {settings["socket"]}")
            exit(0)

        else:
            rootLogger.error("Invalid input.")
            exit(1)
    
    except ValueError:
        rootLogger.error("Input must be an integer.")
        exit(1)
    
    except KeyboardInterrupt:
        rootLogger.info("Keyboard Intrrupted. Shutting down.")
        exit(130)

    except Exception as e:
        rootLogger.error(f"Error at configuration menu in main.py: {e}")
        exit(1)

    try:
        # finally save the file
        with open(f"{SCRIPT_PATH}/settings.json", "w") as file:
            json.dump(settings, file, indent=4)
            rootLogger.debug(f"Saving the {SCRIPT_PATH}/settings.json")
    
    except PermissionError:
        print("Aborting. Are you root?")
    
    exit(0)

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

# If user used --serve options, instead of CLI mode
if argument.serve:
    rootLogger.debug("Entering server mode.")
    from serve import serve_function
    serve_function(local_IP=local_IP, port=PORT)
    exit(0)

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