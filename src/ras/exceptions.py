# --- RAS Controller Exceptions

class RASException(Exception):
    """Specific subclass for RAS Exceptions."""
    pass

class InvalidVersionException(RASException):
    """Exception raised when the provided RAS version is not valid."""
    pass

# --- Config File Exceptions

class ConfigFileException(Exception):
    """"Specific subclass for Config File Exceptions."""
    
class NotAPlanException(ConfigFileException):
    """"Exception raised when the provided filepath for a plan does not follow the plan extension convention."""
    
class NotAFlowException(ConfigFileException):
    """"Exception raised when the provided filepath for a plan does not follow the flow extension convention."""
    
class NotAProjectException(ConfigFileException):
    """"Exception raised when the provided filepath for a plan does not follow the project extension convention."""