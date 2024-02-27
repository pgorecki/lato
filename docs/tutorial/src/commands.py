from datetime import datetime
from uuid import UUID
from lato import Command
from typing import Optional


class CreateTodo(Command):
    """This commands represents an intent to create a new todo"""
    todo_id: UUID
    title: str
    description: str = ""
    due_at: Optional[datetime] = None
    
    
class CompleteTodo(Command):
    """This commands represents an intent to complete an existing todo"""
    todo_id: UUID
    