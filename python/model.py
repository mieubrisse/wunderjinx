class MessageTypes:
    CREATE_TASK = "create_task"

class MessageKeys:
    TYPE = "type"   # MessageTypes
    CREATION_TIMESTAMP = "creation_timestamp"
    BODY = "body"

class CreateTaskKeys:
    ''' Defines the keys in the "body" object '''
    TITLE = "title"
    LIST_ID = "list_id"     # int
    DUE_DATE = "due_date"
    STARRED = "starred"
    NOTE = "note"
