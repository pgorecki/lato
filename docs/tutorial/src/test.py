import uuid
from datetime import date
from lato import Application
from commands import CreateTodo, CompleteTodo
from uuid import UUID
from queries import GetAllTodos, GetSomeTodos


def test_create_and_complete_todo_scenario(app: Application):
    """ This acceptance tests verifies the basic flow of creating and completing a todo """
    app.execute(CreateTodo(todo_id=UUID(int=1), title="Publish the tutorial"))
    
    todos = app.execute(GetAllTodos())
    assert len(todos) == 1
    
    app.execute(CompleteTodo(todo_id=UUID(int=1)))
    assert len(app.execute(GetSomeTodos(completed=True))) == 1
    assert len(app.execute(GetSomeTodos(completed=False))) == 0