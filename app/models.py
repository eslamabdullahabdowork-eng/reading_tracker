# models.py
from pydantic import BaseModel
from enum import Enum

class ReadState(str, Enum):
    done_reading = "done reading"
    not_yet = "not yet"
    want_to = "want to"
    dont_want_to = "dont want to"

class BookState(BaseModel):
    reading_state: ReadState