import http.server
import socketserver
import socket
import os
from scan import scanLogic
from logger import logger_function
from arguments import args
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
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((SOCKET, 80))
    local_IP = s.getsockname()[0]
except OSError:
    rootLogger.error("Network is unreachable. Quitting.")
    exit(1)
except Exception as e:
    rootLogger.error(f"Error at socket connection in main.py: {e}")
    exit(1)
class HTTPHandler(http.server.SimpleHTTPRequestHandler):
    """
    A custom class that inherits http.server.SimpleHTTPRequestHandler class.

    Here is a preview of functions and paths used in this class:

    do_GET:
        - "/" : home page
        - "/api/localip" : private IP of the device
        - "/api/scan" : scanning local network IP addresses
    """
    def do_GET(self):
        url = self.path
        path = "static-files"
        # Home page
        if url == "/":
            self.send_response_only(200)
            rootLogger.info(f"GET {self.path} {self.request_version} 200")
            self.end_headers()
            try:
                with open(f"{path}/index.html", "rb") as html:
                    self.wfile.write(html.read())
            except FileNotFoundError:
                cwd = os.getcwd()
                rootLogger.error(f"{cwd}/{path}/index.html not found.")
        # The favicon is not set yet, Once set the status code should change to 200
        elif url == "/favicon.ico":
            self.send_response_only(404)
            rootLogger.info(f"GET {self.path} {self.request_version} 404")
            self.end_headers()
        # API calls
        elif url == "/api/localip":
            self.send_response_only(200)
            rootLogger.info(f"GET {self.path} {self.request_version} 200")
            self.send_header('Content-Type', 'application/text')
            self.end_headers()
            self.wfile.write(local_IP.encode())
        elif url == "/api/scan":
            self.send_response_only(200)
            rootLogger.info(f"GET {self.path} {self.request_version} 200")
            self.send_header('Content-Type', 'application/text')
            self.end_headers()
            result = scanLogic(local_IP)
            if result == -1:
                self.wfile.write("Error occured. Check the logs file (logs.txt)".encode())
            elif result == 0:
                with open("scan-files/ping_result.txt", "r") as file:
                    ping_result = file.read()
                    self.wfile.write(ping_result.encode())

        # Every other path
        else:
            self.send_response_only(404)
            rootLogger.info(f"GET {self.path} {self.request_version} 404")
            self.end_headers()
            self.wfile.write(b"<h1>Page not found 404</h1>")

if __name__ == "__main__":
    port_is_in_use = True
    while port_is_in_use:
        try:
            rootLogger.info(f"Binding 127.0.0.1:{PORT}...")
            httpd = socketserver.TCPServer(("", PORT), HTTPHandler)
            port_is_in_use = False
            rootLogger.info(f"Server is up. http://127.0.0.1:{PORT}")
            httpd.serve_forever()
        except OSError:
            rootLogger.warning(f"PORT {PORT} is in use.")
            PORT += 1
        except KeyboardInterrupt:
            rootLogger.info("Keyboard Intrrupted. Shutting down.")
            httpd.shutdown()
            s.close()