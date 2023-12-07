from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Message(BaseModel):
    id: UUID = Field(default_factory=uuid4, alias="id")


class Task(Message):
    ...


class Event(Message):
    ...
