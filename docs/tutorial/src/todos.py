from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from commands import CompleteTodo, CreateTodo
from events import TodoWasCompleted
from queries import GetAllTodos, GetSomeTodos, GetTodoDetails

from lato import ApplicationModule, TransactionContext

todos = ApplicationModule("todos")


@dataclass
class TodoModel:
    """Model representing a todo"""

    id: UUID
    title: str
    description: str = ""
    due_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    @property
    def is_completed(self) -> bool:
        return self.completed_at is not None

    def is_due(self, now: datetime) -> bool:
        if self.due_at is None or self.is_completed is False:
            return False
        return self.due_at < now

    def mark_as_completed(self, when: datetime) -> None:
        self.completed_at = when


@dataclass
class TodoReadModel:
    """Read model exposed to the external world"""

    id: UUID
    title: str
    description: str
    is_due: bool
    is_completed: bool


def todo_model_to_read_model(todo: TodoModel, now: datetime) -> TodoReadModel:
    return TodoReadModel(
        id=todo.id,
        title=todo.title,
        description=todo.description,
        is_due=todo.is_due(now),
        is_completed=todo.is_completed,
    )


class TodoRepository:
    """A repository of todos"""

    def __init__(self):
        self.items: list[TodoModel] = []

    def add(self, item: TodoModel) -> None:
        self.items.append(item)

    def get_by_id(self, todo_id: UUID) -> TodoModel:
        for item in self.items:
            if item.id == todo_id:
                return item
        raise ValueError(f"Todo with id {todo_id} does not exist")

    def get_all(self) -> list[TodoModel]:
        return self.items

    def get_all_completed(self):
        return [todo for todo in self.items if todo.is_completed]

    def get_all_not_completed(self):
        return [todo for todo in self.items if not todo.is_completed]


@todos.handler(CreateTodo)
def handle_create_todo(command: CreateTodo, repo: TodoRepository):
    new_todo = TodoModel(
        id=command.todo_id,
        title=command.title,
        description=command.description,
        due_at=command.due_at,
    )
    repo.add(new_todo)


@todos.handler(CompleteTodo)
def handle_complete_todo(
    command: CompleteTodo, repo: TodoRepository, ctx: TransactionContext, now: datetime
):
    a_todo = repo.get_by_id(command.todo_id)
    a_todo.mark_as_completed(now)
    ctx.publish(TodoWasCompleted(todo_id=a_todo.id))


@todos.handler(GetTodoDetails)
def get_todo_details(query: GetTodoDetails, repo: TodoRepository, now: datetime):
    a_todo = repo.get_by_id(query.todo_id)
    return todo_model_to_read_model(a_todo, now)


@todos.handler(GetAllTodos)
def get_all_todos(
    query: GetAllTodos, repo: TodoRepository, now: datetime
) -> list[TodoReadModel]:
    result = repo.get_all()
    return [todo_model_to_read_model(todo, now) for todo in result]


@todos.handler(GetSomeTodos)
def get_some_todos(query: GetSomeTodos, repo: TodoRepository, now: datetime):
    if query.completed is None:
        result = repo.get_all()
    else:
        result = (
            repo.get_all_completed()
            if query.completed
            else repo.get_all_not_completed()
        )

    return [todo_model_to_read_model(todo, now) for todo in result]
