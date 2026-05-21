import logging
from sys import stdout

# Trace level definition
TRACE_LEVEL = 5
logging.addLevelName(TRACE_LEVEL, "TRACE")


def trace(self, msg, *args, **kwargs) -> None:
    if self.isEnabledFor(TRACE_LEVEL):
        self._log(TRACE_LEVEL, msg, args, **kwargs)


logging.Logger.trace = trace


class ColorFormatter(logging.Formatter):
    """
    Applies ANSI color codes to log level names.
    Colors are applied only when the output stream is an
    interactive terminal.
    """

    COLORS = {
        TRACE_LEVEL: "\033[34m",
        logging.DEBUG: "\033[36m",
        logging.INFO: "\033[32m",
        logging.WARNING: "\033[33m",
        logging.ERROR: "\033[31m",
        logging.CRITICAL: "\033[1;31m",
    }
    RESET = "\033[0m"

    def formatMessage(self, record) -> str:
        # Only colorize output if writing to an interactive terminal
        if stdout.isatty():
            color = self.COLORS.get(record.levelno, "")

            # Apply ANSI color escape codes to the level name
            level_name = record.levelname
            colored = f"{color}{level_name}{self.RESET}"

            # Clone the LogRecord to avoid mutating the original record object
            new_record = logging.makeLogRecord(record.__dict__.copy())
            new_record.levelname = colored

            return super().formatMessage(new_record)

        # Fallback - No colors for redirected outputs
        return super().formatMessage(record)


def get_core_logger(
    log_output: str | None = None, use_color: bool = True
) -> logging.Logger:
    """
    Create and modify the core logger.

    Args:
        log_output (str|None): Output path for storing logs; `None` if not provided.
        use_color (bool): Whether to enable colored console log output.

    Returns:
        Logger: The core logger.
    """
    console_format = "%(asctime)s [%(levelname)s] %(message)s"
    file_format = "%(asctime)s [%(levelname)s] %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    core_logger = logging.getLogger("core")

    # Prevent duplicated logging
    if not core_logger.handlers:
        console_handler = logging.StreamHandler()
        if use_color:
            console_handler.setFormatter(
                ColorFormatter(fmt=console_format, datefmt=date_format)
            )
        else:
            console_handler.setFormatter(
                logging.Formatter(file_format, datefmt=date_format)
            )
        console_handler.setLevel(logging.NOTSET)

        if log_output:
            file_handler = logging.FileHandler(log_output)
            file_handler.setFormatter(
                logging.Formatter(file_format, datefmt=date_format)
            )
            file_handler.setLevel(logging.NOTSET)
            core_logger.addHandler(file_handler)

        core_logger.addHandler(console_handler)

        core_logger.setLevel(logging.INFO)

    return core_logger
