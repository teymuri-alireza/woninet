class PingUtilityNotFound(Exception):
    """Raised if the ping command is not found on PATH."""


class DatabaseConnectionFailed(Exception):
    """Raised when the database connection is failed."""
