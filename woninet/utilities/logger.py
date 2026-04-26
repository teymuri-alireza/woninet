import logging

# Trace level definition
TRACE_LEVEL = 5
logging.addLevelName(TRACE_LEVEL, "TRACE")


def trace(self, msg, *args, **kwargs):
    if self.isEnabledFor(TRACE_LEVEL):
        self._log(TRACE_LEVEL, msg, args, **kwargs)


logging.Logger.trace = trace


def logger_function() -> logging.Logger:
    """
    Returns the rootLogger.
    """
    consoleLogFormat = "%(message)s"
    fileLogFormat = "%(asctime)s [%(levelname)s] %(message)s"
    dateFormat = "%Y-%m-%d %H:%M:%S"

    rootLogger = logging.getLogger("core")

    if not rootLogger.handlers:
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(
            logging.Formatter(fmt=consoleLogFormat, datefmt=None)
        )
        consoleHandler.setLevel(logging.NOTSET)

        fileHandler = logging.FileHandler("logs.txt")
        fileHandler.setFormatter(logging.Formatter(fileLogFormat, datefmt=dateFormat))
        fileHandler.setLevel(logging.NOTSET)

        rootLogger.addHandler(consoleHandler)
        rootLogger.addHandler(fileHandler)

        rootLogger.setLevel(logging.INFO)

    return rootLogger
