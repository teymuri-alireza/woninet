import json
import logging
import datetime
# global variables
SCRIPT_PATH = "/usr/local/lib/.pymonitor"

def logger_function() -> logging.Logger:
    """
    Uses a logging format similar to the method send_request() in the class
    http.server.SimpleHTTPRequestHandler

    This function uses datetime.datetime.now and a list of month names
    to indicate the current month.

    The log output destination will be fethed from settings.json file.

    1 means stdout only, 2 means file only, 3 means stdout and file.
    """
    monthNumber = datetime.datetime.now()
    monthList = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthValue = monthList[monthNumber.month - 1]

    fileLogFormat = "%(asctime)s - %(levelname)s - %(message)s"
    consoleLogFormat = "%(asctime)s - %(message)s"

    dateFormat = f"[%d/{monthValue}/%Y %H:%M:%S]"
    rootLogger = logging.getLogger()

    if not rootLogger.handlers:
        try:
            # read settings.json
            with open(f"{SCRIPT_PATH}/settings.json", "r") as file:
                settings = json.load(file)
            log_settings = settings["log_output"]

            if log_settings in [2, 3]:
                try:
                    fileHandler = logging.FileHandler(filename=f"{SCRIPT_PATH}/logs.txt")
                    fileHandler.setFormatter(logging.Formatter(fmt=fileLogFormat, datefmt=dateFormat))
                    fileHandler.setLevel(logging.DEBUG)
                    rootLogger.addHandler(fileHandler)

                except PermissionError:
                    print("Are you root?")
                    exit(1)
            
            if log_settings in [1, 3]:
                consoleHandler = logging.StreamHandler()
                consoleHandler.setFormatter(logging.Formatter(fmt=consoleLogFormat, datefmt=dateFormat))
                consoleHandler.setLevel(logging.INFO)
                rootLogger.addHandler(consoleHandler)

            rootLogger.setLevel(logging.DEBUG)
        
        except json.JSONDecodeError as e:
            rootLogger.error(f"Error at logger.py: {e}")
            exit(1)
    
    return rootLogger