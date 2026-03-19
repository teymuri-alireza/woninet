"""
This is the main entry point of the script. Argumment handlers, configuration settings and CLI mode are
processed in this file. The server option, loggings, argument definitions and scan logic are written in other files.
For more info check out the documentation.md file
"""

import socket
import json
import os

# global variables
PORT = 8000
SCRIPT_PATH = "/usr/local/lib/.pymonitor"

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
            "log_output": 3,
            "socket": "8.8.8.8"
        }
        with open(f"{SCRIPT_PATH}/settings.json", "w") as file:
            json.dump(settings_structure, file, indent=4)
    
    except PermissionError:
        print("Are you root?")
        exit(1)

# import utilities after checking settings to prevent unplanned PermissionError
from scan import scan_logic
from utilities.logger import logger_function
from utilities.arguments import args

# get logger configuration
rootLogger = logger_function()

# fetch socket from the settings
with open(f"{SCRIPT_PATH}/settings.json", "r") as file:
    settings = json.load(file)
SOCKET = settings["socket"]

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
        global PORT
        PORT = int(port)

# calling argument handler
argument = args(set_socket=set_socket, set_port=set_port)

# handle the --version argument
if argument.version:
    from utilities.version import show_version
    print(show_version())
    exit(0)

# enter configuration settings
if argument.config:
    rootLogger.debug("Entering configuration settings.")
    
    # ask for user's input
    menu = """1. Manage known IP list: Only unknown IP addresses will be shown in the ping result.
2. Manage log output.
3. Change socket value permanently (for private IP determination)
4. Show current settings.
0. exit
choose: """
    try:
        choice = int(input(menu))

        if choice == 0:
            exit(0)
    
        elif choice == 1:
            print("Known IP settings:")
            known_ip = input("\tEnter your IP (only one value): ")
            settings["known_ip"].append(known_ip)
            rootLogger.info(f"Adding {known_ip} to known ip list.")
        
        elif choice == 2:
            print("Log settings:")
            print("""\t1. stdout only\n\t2. file only\n\t3. stdout and file\n\t0. Exit""")
            print("\tNote: Logs are an important part of the app. choose wisely.")
            log_output = input("\tchoose: ")

            if log_output not in ["1", "2", "3", "0"]:
                print("Invalid input")
                exit(1)
            else:
                if log_output == "0":
                    exit(0)
                
                settings["log_output"] = int(log_output)
                rootLogger.info(f"Changing log_output value to {log_output}.")

        elif choice == 3:
            print("Socket settings:")
            print("\tCurrent value: " + settings["socket"])
            new_socket = input("\tNew value: (0 to quit) ")
            
            if new_socket == "0":
                exit(0)
            
            settings["socket"] = new_socket
            rootLogger.info(f"Changing socket value to {new_socket}")

        elif choice == 4:
            rootLogger.info("Requested printing settings.")
            print("Known IP list: ", end="")
            if settings["known_ip"] == []:
                print("-")
            else:
                for ip in settings["known_ip"]:
                    print(ip, end=" - ")
                
                print() # to increase readability
            
            print(f"Log output: {settings["log_output"]}")

            print(f"Socket value: {settings["socket"]}")

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

    # finally save the file
    with open(f"{SCRIPT_PATH}/settings.json", "w") as file:
        json.dump(settings, file, indent=4)
    
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
    from serve import serve_function
    serve_function(local_IP=local_IP, port=PORT)
    exit(0)

# the CLI mode
rootLogger.debug("Entering CLI mode scanner.")
rootLogger.info(f"Your private IP: {local_IP}")

menu = """1. Scan the network
0. Exit
Choose: """
while True:
    try:
        choice = input(menu)

        if int(choice) == 0:
            rootLogger.info("Quitting.")
            exit(0)
        
        elif int(choice) == 1:
            rootLogger.info("Starting scan...")
            result = scan_logic(local_IP)
            
            if result == -1:
                # The error will be printed from the scan_logic function
                exit(1)
            
            elif result == 0:
                with open(f"{SCRIPT_PATH}/scan-files/ping_result.txt", "r") as file:
                    ping_result = file.read()
                    
                    # if no result was found
                    if ping_result.strip() == "":
                        print("No result!")
                    else:
                        print(ping_result)
        
        else:
            print("Try again.")
    
    except ValueError:
        rootLogger.error("Input must be an integer.")
    
    except KeyboardInterrupt:
        rootLogger.info("Keyboard Intrrupted. Shutting down.")
        exit(130)
    
    except Exception as e:
        rootLogger.error(f"Error occured: {e}")
        exit(1)