First Module
============

Conceptually, the application module is a collection of message handlers. The handler is a function that accepts a message, and other
dependencies required for message processing. It then processes the message in a specific way, 
typically by reading some objects (in our case todo items) from a database, or changing their state (i.e. updating the state).
As a side effect of message processing, new events may be published, which successively are handled by event handlers.

Declaring a module
------------------

Lets start by declaring the core module of our application - `todos` module. The ``ApplicationModule`` employs a decorator pattern to 
link handlers for different messages within one module.

.. literalinclude:: src/todos.py
   :start-at: from lato import ApplicationModule
   :end-at: todos = ApplicationModule

Now, given the ``TodoModel`` and ``TodoRepository``, we are finally ready to implement all the handlers. 
Let's go through the handlers one by one:

Command handlers
----------------

Below is the handler for creating a new todo. The first argument is the command, and second one is the todo repository.
The repository serves as a dependency and it will be provided by the application at the time of handler execution. 

.. literalinclude:: src/todos.py
   :pyobject: handle_create_todo

One of the core features of *Lato* is the ability to automatically inject handler dependencies - see :ref:`dependency_injection` for more details.

Publishing events
-----------------

A command handler for completing a todo follows a similar pattern. However, it introduces to additional dependencies:

.. literalinclude:: src/todos.py
   :pyobject: handle_complete_todo

The dependencies are:

- ``ctx`` - `TransactionContext` object. :ref:`transaction_context` is a core concept in *lato*, responsible for managing a context in which messages are being processed. Here we are using it to publish an event.
- ``now`` - the current datetime.

The ``ctx.publish`` method is used to publish the event to any subscriber that is interested in its processing. In this case
we are emitting ``TodoWasCompleted``, which could handled both ``Analytics`` module to update productivity stats, 
and by ``Notifications`` (i.e. to send an email). 

.. note::
   Events play a crucial role in achieving loose coupling by allowing 
   communication between different parts of the system without direct dependencies. When one handler publishes a event, 
   it doesn't need to know which other handlers are interested in that event. Thus, the sender and receiver are decoupled.



Query handlers
--------------

The role *query handlers* is to retrieve data, without introducing any changes to the state of the application.
By separating the query handling logic from command handling logic, we can optimize the data retrieval process, and achieve a higher degree of decoupling between the 
components responsible for reading and writing.

Here is the handler for retrieving all todos:

.. literalinclude:: src/todos.py
   :pyobject: get_all_todos

and the handler from retrieving completed and not completed todos, depending on the query payload:

.. literalinclude:: src/todos.py
   :pyobject: get_some_todos

It's worth noting that both query handlers return read models. Here is the implementation of mapping from a domain model to a read model:

.. literalinclude:: src/todos.py
   :pyobject: todo_model_to_read_model

Let's wrap it up:

.. literalinclude:: src/todos.py
