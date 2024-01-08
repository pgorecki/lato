from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Message(BaseModel):
    id: UUID = Field(default_factory=uuid4, alias="id")

    def get_alias(self):
        return self.__class__


class Task(Message):
    ...


class Event(Message):
    ...
