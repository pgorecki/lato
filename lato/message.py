from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Task(BaseModel):
    task_id: UUID = Field(default_factory=uuid4, alias="task_id")


class Event(BaseModel):
    event_id: UUID = Field(default_factory=uuid4, alias="event_id")
