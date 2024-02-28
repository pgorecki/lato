from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Message(BaseModel):
    id: UUID = Field(default_factory=uuid4, alias="id")

    def get_alias(self):
        return self.__class__


class Command(Message):
    """Base class for all commands"""

    ...


class Query(Message):
    """Base class for all queries"""

    ...


class Event(Message):
    """Base class for all events"""

    ...
