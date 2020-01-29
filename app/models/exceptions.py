class DatabaseError(Exception):
    """Raised, when the queried user information is incomplete or not present"""
    pass

class UserNotFoundError(DatabaseError):
    """Raised when user does not exist in database"""
    pass

class UserNotRegisteredError(DatabaseError):
    """Raised when user exists in database but has no chat handle registered"""
    pass