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

    The default output is console (stdout) and the level is info.
    """
    monthNumber = datetime.datetime.now()
    monthList = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthValue = monthList[monthNumber.month - 1]

    consoleLogFormat = "%(asctime)s - %(message)s"
    dateFormat = f"[%d/{monthValue}/%Y %H:%M:%S]"

    rootLogger = logging.getLogger()

    if not rootLogger.handlers:

        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(logging.Formatter(fmt=consoleLogFormat, datefmt=dateFormat))
        consoleHandler.setLevel(logging.DEBUG)
        rootLogger.addHandler(consoleHandler)

        rootLogger.setLevel(logging.INFO)

    return rootLogger