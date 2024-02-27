from uuid import UUID
from commands import CreateTodo, CompleteTodo
from queries import  GetAllTodos
from application import create_app

app = create_app()

app.execute(CreateTodo(todo_id=UUID(int=1), title="Publish the tutorial"))

all_todos = app.execute(GetAllTodos())
print(all_todos)

app.execute(CompleteTodo(todo_id=UUID(int=1)))

all_todos = app.execute(GetAllTodos())
print(all_todos)