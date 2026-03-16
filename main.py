import socket
from scan import scan_logic
from utilities.logger import logger_function
from utilities.arguments import args
# get logger configuration
rootLogger = logger_function()
# global variables
SOCKET = "8.8.8.8"
PORT = 8000
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
menu = """
1. Scan the network
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
                with open("scan-files/ping_result.txt", "r") as file:
                    ping_result = file.read()
                    print(ping_result[0:-1]) # Remove trailing newline
        else:
            print("Try again.")
    except ValueError:
        print("Input must be an integer.")
    except KeyboardInterrupt:
        rootLogger.info("Keyboard Intrrupted. Shutting down.")
        exit(130)
    except Exception as e:
        print(f"Error occured: {e}")