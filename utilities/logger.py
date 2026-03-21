import logging

def logger_function() -> logging.Logger:
    """
    Returns the rootLogger, which uses a simple format for logging.

    The default output is console (stdout) and the level is info.
    """
    consoleLogFormat = "%(message)s"

    rootLogger = logging.getLogger()

    if not rootLogger.handlers:

        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(logging.Formatter(fmt=consoleLogFormat, datefmt=None))
        consoleHandler.setLevel(logging.DEBUG)
        rootLogger.addHandler(consoleHandler)

        rootLogger.setLevel(logging.INFO)

    return rootLogger