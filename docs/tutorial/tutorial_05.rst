Putting all things together
===========================

Up to this point, we have defined messages, their corresponding handlers, and organized them into modules. 
Now it's finally time to put everything together.

Creating an application
-----------------------

Below is the factory function for the application. The *kwargs* in the constructor are the dependencies we used earlier across the modules: 
``TodoRepository``, ``NotificationService``, and ``TodosCounter``. Next, modules are linked to the app using ``app.include_submodule()``.
Finally, the transaction middleware is configured using ``on_enter_transaction_context``, ``on_exit_transaction_context``, 
and ``transaction_middleware`` decorators. 

.. literalinclude:: src/application.py

In ``on_enter_transaction_context``, a transaction-level dependency ``now`` is being set. This means that every time a new command is
executed using ``app.execute()``, a new value for ``now`` will be passed to handlers that require it. 

The last piece we are missing to run our test is the ``conftest.py`` implementing the ``app`` fixture:

.. literalinclude:: src/conftest.py

We could also run the app from the command line using the following script:

.. testsetup:: *
    
    import sys
    from os import sep
    doc_root = sys.path[0]
    tutorial_src_root = sep.join([doc_root, 'tutorial', 'src'])
    sys.path.insert(0, tutorial_src_root)

.. testcode::

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

And the output is: 

.. testoutput::

    Begin transaction
    Executing todos.handle_create_todo(CreateTodo)
     todos stats: 0/0
    Result from todos.handle_create_todo: None
    Executing analytics.handle_create_todo(CreateTodo)
     todos stats: 0/1
    Result from analytics.handle_create_todo: None
    End transaction
    Begin transaction
    Executing todos.get_all_todos(GetAllTodos)
     todos stats: 0/1
    Result from todos.get_all_todos: [TodoReadModel(id=UUID('00000000-0000-0000-0000-000000000001'), title='Publish the tutorial', description='', is_due=False, is_completed=False)]
    End transaction
    [TodoReadModel(id=UUID('00000000-0000-0000-0000-000000000001'), title='Publish the tutorial', description='', is_due=False, is_completed=False)]
    Begin transaction
    Executing todos.handle_complete_todo(CompleteTodo)
    Executing notifications.on_todo_was_completed(TodoWasCompleted)
    Executing todos.get_todo_details(GetTodoDetails)
     todos stats: 0/1
    Result from todos.get_todo_details: TodoReadModel(id=UUID('00000000-0000-0000-0000-000000000001'), title='Publish the tutorial', description='', is_due=False, is_completed=True)
    TodoReadModel(id=UUID('00000000-0000-0000-0000-000000000001'), title='Publish the tutorial', description='', is_due=False, is_completed=True)
    A todo Publish the tutorial was completed
     todos stats: 0/1
    Result from notifications.on_todo_was_completed: None
    Executing analytics.on_todo_was_completed(TodoWasCompleted)
     todos stats: 1/1
    Result from analytics.on_todo_was_completed: None
     todos stats: 1/1
    Result from todos.handle_complete_todo: None
    End transaction
    Begin transaction
    Executing todos.get_all_todos(GetAllTodos)
     todos stats: 1/1
    Result from todos.get_all_todos: [TodoReadModel(id=UUID('00000000-0000-0000-0000-000000000001'), title='Publish the tutorial', description='', is_due=False, is_completed=True)]
    End transaction
    [TodoReadModel(id=UUID('00000000-0000-0000-0000-000000000001'), title='Publish the tutorial', description='', is_due=False, is_completed=True)]

Understanding the transaction context
-------------------------------------

When the command is executed via ``app.execute()``, transaction middlewares fire from top to bottom. In our case, ``logging_middleware`` is called first. 
Upon reaching its ``call_next()``, the ``analytics_middleware`` is called. As this is the last middleware, it's ``call_next`` passes the
execution to the the handler. When the handler execution finishes, middlewares resume execution from bottom to top.

Next, let's see how to integrate the application with a `FastAPI` server.
