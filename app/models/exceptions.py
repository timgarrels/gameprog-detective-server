class DatabaseError(Exception):
    """General Database Error (missing or incomplete entries)"""
    pass

class UserNotFoundError(DatabaseError):
    """Raised when user does not exist in database"""
    pass

class UserNotRegisteredError(DatabaseError):
    """Raised when user exists in database but has no chat handle registered"""
    pass