import http.server
import socketserver
import json
import os
from scan import scan_logic
from utilities.logger import logger_function
from utilities.validate_ip import validate_ip

# get logger configuration
rootLogger = logger_function()

# global variables
SCRIPT_PATH = "/usr/local/lib/pymonitor"
# scan result path will be always stored at /usr/local/lib
SCAN_RESULT_PATH = "/usr/local/lib/pymonitor"

# check if index.html exist in the script path, else use the current directory
try:
    with open(f"{SCRIPT_PATH}/static-files/index.html", "r") as file:
        pass
except FileNotFoundError:
    rootLogger.debug(f"Using {os.getcwd()} instead of {SCRIPT_PATH}")
    SCRIPT_PATH = os.getcwd()

def serve_function(local_IP: str, port: int):
    """
    This function is called if user used the --serve option
    and includes the HTTPHandler class and while loop for running the server.
    
    Parameters:
        local_IP (str) : Private IP of the device.

        port (int) : The port number for serving the server.
    """
    class HTTPHandler(http.server.SimpleHTTPRequestHandler):
        """
        A custom class that inherits http.server.SimpleHTTPRequestHandler class.
        This class gets the basic information like device's private IP
        and the server's port from the main.py file.

        Here is a preview of functions and paths used in this class:

        do_GET:
            - "/" : The home page
            - "/style.css" : Serves contents of css file
            - "/app.js" : Serves contents of js file
            - "/api/localip" : Sends the private IP of the device to the client
            - "/api/scan" : Scanning local network IP addresses
            - "/api/fetch-settings" : Reads the current settings and sends to the client
        
        do_POST:
            - "/api/update-settings" : Updates the configuration settings
        """
        def do_GET(self):
            url = self.path
            static_files = f"{SCRIPT_PATH}/static-files"
            
            # Home page
            if url == "/":
                self.send_response_only(200)
                rootLogger.info(f"GET {url} {self.request_version} 200")
                self.end_headers()
                try:
                    with open(f"{static_files}/index.html", "rb") as html:
                        self.wfile.write(html.read())
                except FileNotFoundError:
                    rootLogger.error(f"{static_files}/index.html not found.")
            
            # The favicon is not set yet, Once set the status code should change to 200
            elif url == "/favicon.ico":
                self.send_response_only(404)
                rootLogger.info(f"GET {url} {self.request_version} 404")
                self.end_headers()
            
            # serving contents of css
            elif url == "/style.css":
                with open(f"{static_files}/style.css", "rb") as css:
                    self.send_response_only(200)
                    rootLogger.info(f"GET {url} {self.request_version} 200")
                    self.send_header("Content-type", "text/css")
                    self.end_headers()
                    self.wfile.write(css.read())
            
            # serving contents of javascript
            elif url == "/app.js":
                with open(f"{static_files}/app.js", "rb") as js:
                    self.send_response_only(200)
                    rootLogger.info(f"GET {url} {self.request_version} 200")
                    self.send_header("Content-type", "text/js")
                    self.end_headers()
                    self.wfile.write(js.read())
            
            # API calls
            elif url == "/api/localip":
                self.send_response_only(200)
                rootLogger.info(f"GET {url} {self.request_version} 200")
                self.send_header('Content-Type', 'application/text')
                self.end_headers()
                self.wfile.write(local_IP.encode())
            
            elif url == "/api/scan":
                self.send_response_only(200)
                rootLogger.info(f"GET {url} {self.request_version} 200")
                self.send_header('Content-Type', 'application/text')
                self.end_headers()
                result = scan_logic(local_IP)
                if result == -1:
                    self.wfile.write("Error occured. Check the logs file (logs.txt)".encode())
                elif result == 0:
                    with open(f"{SCAN_RESULT_PATH}/scan-files/ping_result.txt", "r") as file:
                        ping_result = file.read()
                        self.wfile.write(ping_result.encode())

            elif url == "/api/fetch-settings":
                self.send_response_only(200)
                rootLogger.info(f"GET {url} {self.request_version} 200")
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                try:
                    with open(f"{SCAN_RESULT_PATH}/settings.json", "rb") as settings:
                        self.wfile.write(settings.read())
                except PermissionError:
                    rootLogger.error("You need root access!")

            # Every other path
            else:
                self.send_response_only(404)
                rootLogger.info(f"GET {self.path} {self.request_version} 404")
                self.end_headers()
                self.wfile.write(b"<h1>Page not found 404</h1>")

        def do_POST(self):
            url = self.path
            
            # updating settings
            if url == "/api/update-settings":
                try:
                    content_length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(content_length)
                    data = json.loads(body.decode())

                    new_known_ip = data["known_ip_list_input"]
                    new_socket = data["socket_value_input"]
                
                    with open(f"{SCAN_RESULT_PATH}/settings.json", "r") as file:
                        settings = json.load(file)
                    
                    if new_known_ip.strip() != "":
                        seperate_input = new_known_ip.split(",")
                        for ip in seperate_input:
                            ip = ip.strip()
                            if ip == "":
                                continue

                            # remove IP address, if they exist
                            if ip in settings["known_ip"]:
                                settings["known_ip"].remove(ip)
                                rootLogger.debug(f"Removing {ip} from known ip list.")
                            else:
                                # validation and adding
                                if validate_ip(ip):
                                    settings["known_ip"].append(ip)
                                    rootLogger.debug(f"Adding {ip} to known ip list.")
                                else:
                                    # if error occured
                                    self.send_response_only(400)
                                    self.send_header('Content-Type', 'application/json')
                                    self.end_headers()
                                    return

                        # sorting values
                        settings["known_ip"].sort()

                    if new_socket.strip() != "":
                        settings["socket"] = new_socket
                        rootLogger.debug(f"Changing socket value to {new_socket}")
                    
                    with open(f"{SCAN_RESULT_PATH}/settings.json", "w") as file:
                        json.dump(settings, file, indent=4)
                    
                    self.send_response_only(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()

                    rootLogger.info(f"POST {url} {self.request_version} 200")

                except Exception as e:
                    self.send_response_only(500)
                    rootLogger.error(f"POST {url} {self.request_version} 500 - Error: {e}")
            
    # Running the server
    port_is_in_use = True
    while port_is_in_use:
        try:
            rootLogger.info(f"Binding 127.0.0.1:{port}...")
            httpd = socketserver.TCPServer(("127.0.0.1", port), HTTPHandler)
            port_is_in_use = False
            rootLogger.info(f"Server is up. http://127.0.0.1:{port}")
            httpd.serve_forever()
        
        except OSError:
            rootLogger.warning(f"PORT {port} is in use.")
            port += 1
        
        except KeyboardInterrupt:
            rootLogger.info("Keyboard Intrrupted. Shutting down.")
            httpd.shutdown()
        
        except Exception as e:
            rootLogger.error(f"Error at serve.py: {e}")