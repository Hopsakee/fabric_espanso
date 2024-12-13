"""Custom exceptions for the fabric-to-espanso application."""

class FabricToEspansoError(Exception):
    """Base exception for all fabric-to-espanso errors."""
    pass

class DatabaseError(FabricToEspansoError):
    """Base exception for database-related errors."""
    pass

class DatabaseConnectionError(DatabaseError):
    """Raised when unable to connect to the database."""
    pass

class DatabaseInitializationError(DatabaseError):
    """Raised when database initialization fails."""
    pass

class CollectionError(DatabaseError):
    """Raised when there's an error with collection operations."""
    pass

class ConfigurationError(FabricToEspansoError):
    """Raised when there's an error in the configuration."""
    pass

class NotImplementedError(FabricToEspansoError):
    """Raised when a feature is not implemented."""
    pass