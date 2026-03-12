import http.server
import socketserver
import datetime
import logging
import socket
import json
import os
from scan import scanLogic
from logger import logger_function
# get logger configuration
rootLogger = logger_function()
# get local IP address
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
local_IP = s.getsockname()[0]
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
            resullt = scanLogic(local_IP)
        # Every other path
        else:
            self.send_response_only(404)
            rootLogger.info(f"GET {self.path} {self.request_version} 404")
            self.end_headers()
            self.wfile.write(b"<h1>Page not found 404</h1>")

if __name__ == "__main__":
    PORT = 8000
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