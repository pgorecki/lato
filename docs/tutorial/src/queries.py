from uuid import UUID
from lato import Query
from typing import Optional
from datetime import datetime


class GetAllTodos(Query):
    """A query to get a list of all todos"""
    pass


class GetSomeTodos(Query):
    """A query to get specific subset of todos"""
    completed: Optional[bool]
    
    
class GetTodoDetails(Query):
    """A query to get details of a single todo"""
    todo_id: UUID
