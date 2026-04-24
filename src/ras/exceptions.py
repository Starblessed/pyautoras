class RASException(Exception):
    """Specific subclass for RAS Exceptions."""
    pass

class InvalidVersionException(RASException):
    """Exception raised when the provided RAS version is not valid."""
    pass
