class StoryException(Exception):
    """General exception that prevent the story progression"""
    pass

class UserReplyInvalid(StoryException):
    """Raised when a given user reply is not valid for the current story point"""
    pass

class StoryPointInvalid(StoryException):
    """Raised when the current story point is to be set to an non existent story point"""