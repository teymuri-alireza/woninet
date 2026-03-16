import json
import logging
import datetime

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

    logFormat = "%(asctime)s \"%(message)s"
    dateFormat = f"[%d/{monthValue}/%Y %H:%M:%S]"
    rootLogger = logging.getLogger()

    if not rootLogger.handlers:
        # read settings.json
        with open("settings.json", "r") as file:
            settings = json.load(file)
        log_settings = settings["log_format"]

        if log_settings in [2, 3]:
            fileHandler = logging.FileHandler(filename="logs.txt")
            fileHandler.setFormatter(logging.Formatter(fmt=logFormat, datefmt=dateFormat))
            fileHandler.setLevel(logging.INFO)
            rootLogger.addHandler(fileHandler)
        
        if log_settings in [1, 3]:
            consoleHandler = logging.StreamHandler()
            consoleHandler.setFormatter(logging.Formatter(fmt=logFormat, datefmt=dateFormat))
            consoleHandler.setLevel(logging.INFO)
            rootLogger.addHandler(consoleHandler)

        rootLogger.setLevel(logging.INFO)
    
    return rootLogger