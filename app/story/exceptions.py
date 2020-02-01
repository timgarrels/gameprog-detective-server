class StoryException(Exception):
    """General exception that prevent the story progression"""
    pass

class UserReplyInvalid(StoryException):
    """Raised when a given user reply is not valid for the current story point"""
    pass
