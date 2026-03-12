import logging
import datetime

def logger_function() -> logging.Logger:
    """
    Uses a logging format similar to the method send_request() in the class
    http.server.SimpleHTTPRequestHandler

    This function uses datetime.datetime.now and a list of month names
    to indicate the current month.

    The outputs are printed in both stdout and a file (logs.txt)
    """
    monthNumber = datetime.datetime.now()
    monthList = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthValue = monthList[monthNumber.month - 1]

    logFormat = "%(asctime)s \"%(message)s"
    dateFormat = f"[%d/{monthValue}/%Y %H:%M:%S]"
    rootLogger = logging.getLogger()

    if not rootLogger:
        fileHandler = logging.FileHandler(filename="logs.txt")
        fileHandler.setFormatter(logging.Formatter(fmt=logFormat, datefmt=dateFormat))
        fileHandler.setLevel(logging.INFO)
        
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(logging.Formatter(fmt=logFormat, datefmt=dateFormat))
        consoleHandler.setLevel(logging.INFO)

        rootLogger.addHandler(consoleHandler)
        rootLogger.addHandler(fileHandler)
        rootLogger.setLevel(logging.INFO)
    
    return rootLogger