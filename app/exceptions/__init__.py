# define Python user-defined exceptions
from pydantic import PydanticValueError, BaseModel


class Error(PydanticValueError):
    """Base class for other exceptions"""
    code: str = ''
    msg_template: str = ''
    holder = ''

    def message(self, *args):
        return self.msg_template.format(*args if args else self.holder)


class OutputError(BaseModel):
    msg_template: str = ''


class GeneralError(Error):
    code = 'general_error'
    msg_template = "Unexpected error."


class UserNotUnique(Error):
    code = 'user_not_unique'
    msg_template = "The user '{}' already exists."


class UserNotFound(Error):
    code = 'user_not_found'
    msg_template = "The user '{}' was not found."


class WatcherNotFound(Error):
    code = 'watcher_not_found'
    msg_template = "The watcher '{}' was not found."
