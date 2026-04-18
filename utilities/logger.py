import logging

def logger_function() -> logging.Logger:
    """
    Returns the rootLogger.
    """
    consoleLogFormat = "%(message)s"
    fileLogFormat = "%(asctime)s - %(levelname)s - %(message)s"
    dateFormat = "%Y-%m-%d %H:%M:%S"

    rootLogger = logging.getLogger()

    if not rootLogger.handlers:

        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(logging.Formatter(fmt=consoleLogFormat, datefmt=None))
        consoleHandler.setLevel(logging.NOTSET)

        fileHandler = logging.FileHandler("logs.txt")
        fileHandler.setFormatter(logging.Formatter(fileLogFormat, datefmt=dateFormat))
        fileHandler.setLevel(logging.NOTSET)

        rootLogger.addHandler(consoleHandler)
        rootLogger.addHandler(fileHandler)

        rootLogger.setLevel(logging.INFO)

    return rootLogger