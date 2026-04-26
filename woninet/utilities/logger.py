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
    Returns the root logger.
    """
    console_format = "%(asctime)s [%(levelname)s] %(message)s"
    file_format = "%(asctime)s [%(levelname)s] %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    root_logger = logging.getLogger("core")

    if not root_logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter(fmt=console_format, datefmt=date_format)
        )
        console_handler.setLevel(logging.NOTSET)

        file_handler = logging.FileHandler("logs.txt")
        file_handler.setFormatter(logging.Formatter(file_format, datefmt=date_format))
        file_handler.setLevel(logging.NOTSET)

        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)

        root_logger.setLevel(logging.INFO)

    return root_logger
