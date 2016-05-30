# TODO These should probably be in a config file somewhere
DATE_FORMAT = "%Y-%m-%d"
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

class MessageTypes:
    CREATE_TASK = "create_task"
    # TODO Update, delete, etc.

class MessageKeys:
    TYPE = "type"   # MessageTypes
    CREATION_TIMESTAMP = "creation_timestamp"
    BODY = "body"

class CreateTaskKeys:
    ''' Defines the keys in the "body" object '''
    TITLE = "title"
    LIST_NAME = "list_name" # User-entered text
    DUE_DATE = "due_date"
    STARRED = "starred"
    NOTE = "note"
