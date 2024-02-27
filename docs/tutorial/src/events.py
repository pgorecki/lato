from uuid import UUID
from lato import Event


class TodoWasCompleted(Event):
    """Event to indicate that the todo was completed"""
    todo_id: UUID

