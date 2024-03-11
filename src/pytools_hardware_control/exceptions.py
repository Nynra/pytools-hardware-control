

class ConnectionError(Exception):
    """Raised when a connection to a device cannot be established."""
    pass


class TimeoutError(Exception):
    """Raised when a device does not respond in time."""
    pass


class UnknownCommandError(Exception):
    """Raised when an unknown command is sent to a device."""
    pass


class ValueOutOfBoundsError(Exception):
    """Raised when a value is out of bounds."""
    pass


class CurrentLimitError(Exception):
    """Raised when a current limit is reached in function generator mode."""
    pass


class TektronixScopeError(Exception):
    """Exception raised from the TektronixScope class."""

    def __init__(self, mesg):
        self.mesg = mesg

    def __repr__(self):
        return self.mesg

    def __str__(self):
        return self.mesg