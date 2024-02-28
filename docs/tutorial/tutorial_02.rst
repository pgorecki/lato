Building Blocks
===============

In this section we will define the basic building blocks that will be used by the 
core module of the application, namely the `todos` module. 

Domain model
------------

Since the *todos* module is responsible for adding and completing todos, 
we need to define a ``TodoModel`` that will encapsulate all logic related to a todo:

.. literalinclude:: src/todos.py
   :pyobject: TodoModel

From this point we will refer to *TodoModel* instances as todo entities (or entities in short). 

Read model
----------

In addition to a ``TodoModel``, we will also create a corresponding ``TodoReadModel``:

.. literalinclude:: src/todos.py
   :pyobject: TodoReadModel

Why do we need 2 models? ``TodoModel`` serves as a domain model that encapsulates the business logic of a todo entity. 
This model will be modified by command handlers defined within the module. In other words, only the *todos* module has the authority to change the 
state of ``TodoModel`` other modules are not permitted to access it.

On the other hand, ``TodoReadModel`` is exposed outside the *todos* module. Other modules can query the *todos* module and
receive the read model. If other modules need to make changes, they should not directly access it. 
Instead, they should request the modification by sending a message to the todos module.


Todo repository
---------------

Our design pattern of choice for storing and retrieving entities is the *repository pattern*. 

.. note::
   The repository pattern encapsulates the logic for accessing data within an application, 
   providing a layer of abstraction between the data access code and the business logic. By abstracting away the details of data storage and retrieval, it promotes modularity, testability, and flexibility in software design.

In real applications, a repository is commonly associated with a fully-fledged database.
This includes managing DB connections, managing transactions with commit and rollback operations, etc.
However, for the sake of simplicity, we will implement the in-memory ``TodoRepository`` as follows:

.. literalinclude:: src/todos.py
   :pyobject: TodoRepository

Having the basic building blocks in place, we are now ready to implement the `todos` module.
