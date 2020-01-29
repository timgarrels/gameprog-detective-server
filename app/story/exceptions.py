class StoryException(Exception):
    """General exception that prevent the story progression"""
    pass

class CurrentStoryPointNotSet(StoryException):
    """Raised when the current story point of a user is queried, but not set"""
    pass

class UserReplyInvalid(StoryException):
    """Raised when a given user reply is not valid for the current story point"""
    pass

class IncompletedTaskActive(StoryException):
    """Raised when the story cannot be progressed because of an incompleted task"""
    pass
