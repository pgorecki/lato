Additional Modules
==================

Having the *todos* module in place, let's create two additional modules.


Analytics Module
----------------

The *analytics* module has a similar structure to *todos* module. It consists of a ``TodosCounter`` which stores
some basic stats the command handler, and the event handler:

.. literalinclude:: src/analytics.py

It's worth noting that ``CreateTodo`` is handled by two modules now ( *todos* and *analytics*). When the application receives
a this command, both modules will be triggered. In a similar way, multiple modules can respond to one query.
This pattern is called :ref:`message_composition`. 




Notifications Module
--------------------

Notifications module is using a fake ``NotificationService`` to push the message when the ``TodoWasCompleted`` 
is published by the *todos* module. In addition, it demonstrates how *notifications* module is querying *todos* module
to get the title of a todo that has been completed:

.. literalinclude:: src/notifications.py

In particular, the query is dispatched using a ``TransactionContext``, 
which is the context in which the ``TodoWasCompleted`` event was published earlier:

.. literalinclude:: src/todos.py
   :pyobject: handle_complete_todo
   :emphasize-lines: 5

In the next section we will see how modules are wired together into the application, and how the dependencies are provided to messages handlers.