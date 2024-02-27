Commands and Queries
====================

Let's start the tutorial by creating a test to show how to use lato. This test will demonstrate how to 
interact with any app built with *lato*. We're following a CQRS pattern, where you only need to use ``app.execute`` for 
the invocation of commands and queries.

.. note::
    CQRS (Command Query Responsibility Segregation) is an architectural pattern 
    that separates the read and write operations of an application. *Commands* are 
    used to change the state to the application, while *queries* are used read the state.

With help of *pytest*, we can create our our first happy path acceptance test:

.. literalinclude:: src/test.py
    :pyobject: test_create_and_complete_todo_scenario

Running this code requires the `app` fixture, and a bunch of commands (``CreateTodo``, ``CompleteTodo``) and queries (``GetAllTodos``, ``GetSomeTodos``). Let's start with
latter ones.

A commands in lato is `pydantic` data structures with no behavior, which contains all the necessary:

.. literalinclude:: src/commands.py

Take note that the identifier for a new todo, ``todo_id``, is explicitly provided. This simplifies testing 
for the app and aligns with the CQRS pattern. By supplying the id upfront, there's no need to return it, 
and we can eliminate the reliance on the database for id generation.

Queries are similar to commands, note that some of the queries does not require any arguments:

.. literalinclude:: src/queries.py

In the next step we will implement a module responsible for handling the queries and commands.

