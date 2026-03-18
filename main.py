#!/usr/bin/python3

import socket
import json
import subprocess
# global variables
SOCKET = "8.8.8.8"
PORT = 8000
SCRIPT_PATH = "/usr/local/lib/.pymonitor"

# check if settings.json exist
try:
    with open(f"{SCRIPT_PATH}/settings.json", "r") as file:
        pass
except FileNotFoundError:
    try:
        settings_structure = {
            "known_ip": [],
            "log_output": 3
        }
        with open(f"{SCRIPT_PATH}/settings.json", "w") as file:
            json.dump(settings_structure, file, indent=4)
    
    except PermissionError:
        print("Are you root?")
        exit(1)

# import utilities after checking settings
from scan import scan_logic
from utilities.logger import logger_function
from utilities.arguments import args

# get logger configuration
rootLogger = logger_function()
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
# get arguments
argument = args(set_socket=set_socket, set_port=set_port)

# enter configuration settings
if argument.config:
    rootLogger.info("Entering configuration settings.")

    # open settings file anyway
    with open(f"{SCRIPT_PATH}/settings.json", "r") as file:
        settings = json.load(file)
    
    # ask for user's input
    menu = """1. Manage known IP list: Only unknown IP addresses will be shown in the ping result.
2. Manage log output.
3. Show current settings.
0. exit
choose: """
    try:
        choice = int(input(menu))

        if choice == 0:
            rootLogger.info("Quitting configuration settings.")
            exit(0)
    
        elif choice == 1:
            print("Known IP settings:")
            knwon_ip = input("\tEnter your IP (only one value): ")
            settings["known_ip"].append(knwon_ip)
            rootLogger.info(f"Adding {knwon_ip} to known ip list.")
        
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
                    rootLogger.info("Quitting configuration settings.")
                    exit(0)
                
                settings["log_output"] = int(log_output)
                rootLogger.info(f"Changing log_output value to {log_output}.")

        elif choice == 3:
            rootLogger.info("Requested printing settings.")
            print("Known IP list: ", end="")
            if settings["known_ip"] == []:
                print("-")
            else:
                for ip in settings["known_ip"]:
                    print(ip, end=" - ")
            
            print(f"\nLog output: {settings["log_output"]}")

        else:
            rootLogger.error("Invalid input.")
            exit(1)
    
    except ValueError:
        rootLogger.error("Input must be an integer.")
        exit(1)
    
    except KeyboardInterrupt:
        rootLogger.info("Keyboard Intrrupted.")
        exit(130)

    except Exception as e:
        rootLogger.error(f"Error at configuration menu in main.py: {e}")
        exit(1)

    # finally save the file
    with open(f"{SCRIPT_PATH}/settings.json", "w") as file:
        json.dump(settings, file, indent=4)
    
    rootLogger.info("Quitting configuration settings.")
    exit(0)

# get local IP address
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
# If user chose to serve the server instead of the CLI mode
if argument.serve:
    from serve import serve_function
    serve_function(local_IP=local_IP, port=PORT)
    exit(0)

# CLI mode
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
        print("Input must be an integer.")
    except KeyboardInterrupt:
        rootLogger.info("Keyboard Intrrupted. Shutting down.")
        exit(130)
    except Exception as e:
        print(f"Error occured: {e}")