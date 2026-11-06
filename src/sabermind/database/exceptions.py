class DatabaseError(Exception):
    """Base class for database-related exceptions."""

    pass


class ConnectionError(DatabaseError):
    """Exception raised for errors in the database connection."""

    pass


class QueryError(DatabaseError):
    """Exception raised for errors in the database queries."""

    pass
