[![](https://github.com/pgorecki/lato/workflows/Tests/badge.svg)](https://github.com/pgorecki/lato/actions?query=workflow%3ATests)
[![Documentation Status](https://readthedocs.org/projects/lato/badge/?version=latest)](https://lato.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://img.shields.io/pypi/v/lato)](https://pypi.org/project/lato/)
[![Python Versions](https://img.shields.io/pypi/pyversions/lato)](https://pypi.org/project/lato/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://static.pepy.tech/badge/lato/month)](https://pepy.tech/project/lato)

# Lato

Lato is a Python microframework designed for building **modular monoliths** and **loosely coupled** applications.
Based on dependency injection and Python 3.6+ type hints.

---

**Documentation**: <a href="https://lato.readthedocs.io" target="_blank">https://lato.readthedocs.io</a>

**Source Code**: <a href="https://github.com/pgorecki/lato" target="_blank">https://github.com/pgorecki/lato</a>

---

## Features

- **Modularity**: Organize your application into smaller, independent modules for better maintainability.

- **Flexibility**: Loosely couple your application components, making them easier to refactor and extend.

- **Testability**: Easily test your application components in isolation. 

- **Minimalistic**: Intuitive and lean API for rapid development without the bloat.

- **Async Support**: Concurrency and async / await is supported.


## Installation

Install `lato` using pip:

```bash
pip install lato
```

## Quickstart

Here's a simple example to get you started:

```python
from lato import Application, TransactionContext
from uuid import uuid4


class UserService:
    def create_user(self, email, password):
        ...


class EmailService:
    def send_welcome_email(self, email):
        ...


app = Application(
    name="Hello World",
    # dependencies
    user_service=UserService(),
    email_service=EmailService(),
)


def create_user_use_case(email, password, session_id, ctx: TransactionContext, user_service: UserService):
    # session_id, TransactionContext and UserService are automatically injected by `ctx.call`
    print("Session ID:", session_id)
    user_service.create_user(email, password)
    ctx.publish("user_created", email)


@app.handler("user_created")
def on_user_created(email, email_service: EmailService):
    email_service.send_welcome_email(email)


with app.transaction_context(session_id=uuid4()) as ctx:
    # session_id is transaction scoped dependency
    result = ctx.call(create_user_use_case, "alice@example.com", "password")
```


## Example of a modular monolith

Lato is designed to help you build modular monoliths, with loosely coupled modules. This example shows how to 
introduce a structure in your application and how to exchange messages (events) between modules.

Let's imagine that we are building an application that allows the company to manage its candidates, 
employees and projects. Candidates and employees are managed by the `employee` module, while projects are managed by
the `project` module. When a candidate is hired, the `employee` module publishes a `CandidateHired` event, which is handled
by the `employee` module to send a welcome email. When an employee is fired, the `employee` module publishes an 
`EmployeeFired` event, which is handled by both the `employee` and `project` modules to send an exit email and 
to remove an employee from any projects, respectively.

First, let's start with commands that holds all the required information to execute a use case:

```python
# commands.py

from lato import Command


class AddCandidate(Command):
    candidate_id: str
    candidate_name: str


class HireCandidate(Command):
    candidate_id: str


class FireEmployee(Command):
    employee_id: str
    
    
class CreateProject(Command):
    project_id: str
    project_name: str
    
    
class AssignEmployeeToProject(Command):
    employee_id: str
    project_id: str
```

And the events that are published by the application (note that all events are expressed in past tense):

```python
# events.py

from lato import Event


class CandidateHired(Event):
    candidate_id: str


class EmployeeFired(Event):
    employee_id: str
    
    
class EmployeeAssignedToProject(Event):
    employee_id: str
    project_id: str
```

Now let's define the employee module. Each function which is responsible for handling a specific command is decorated
with `employee_module.handler`. Similarly, each function which is responsible for handling a specific event is
decorated with `employee_module.on`.

```python
# employee_module.py

from lato import ApplicationModule
from commands import AddCandidate, HireCandidate, FireEmployee
from events import CandidateHired, EmployeeFired

employee_module = ApplicationModule("employee")


@employee_module.handler(AddCandidate)
def add_candidate(command: AddCandidate, logger):
    logger.info(f"Adding candidate {command.candidate_name} with id {command.candidate_id}")


@employee_module.handler(HireCandidate)
def hire_candidate(command: HireCandidate, publish, logger):
    logger.info(f"Hiring candidate {command.candidate_id}")
    publish(CandidateHired(candidate_id=command.candidate_id))


@employee_module.handler(FireEmployee)
def fire_employee(command: FireEmployee, publish, logger):
    logger.info(f"Firing employee {command.employee_id}")
    publish(EmployeeFired(employee_id=command.employee_id))


@employee_module.handler(CandidateHired)
def on_candidate_hired(event: CandidateHired, logger):
    logger.info(f"Sending onboarding email to {event.candidate_id}")


@employee_module.handler(EmployeeFired)
def on_employee_fired(event: EmployeeFired, logger):
    logger.info(f"Sending exit email to {event.employee_id}")
```

As you can see, some functions have additional parameters (such as `logger` or `publish`) which are automatically 
injected by the application (to be more specific, by a transaction context) upon command or event execution. This allows 
you to test your functions in isolation, without having to worry about dependencies. 

The structure of the project module is similar to the employee module:

```python
# project_module.py

from lato.application_module import ApplicationModule
from commands import CreateProject, AssignEmployeeToProject
from events import EmployeeFired, EmployeeAssignedToProject

project_module = ApplicationModule("project")


@project_module.handler(EmployeeFired)
def on_employee_fired(event: EmployeeFired, logger):
    logger.info(f"Checking if employee {event.employee_id} is assigned to a project")


@project_module.handler(CreateProject)
def create_project(command: CreateProject, logger):
    logger.info(f"Creating project {command.project_name} with id {command.project_id}")
    
    
@project_module.handler(AssignEmployeeToProject)
def assign_employee_to_project(command: AssignEmployeeToProject, publish, logger):
    logger.info(f"Assigning employee {command.employee_id} to project {command.project_id}")
    publish(EmployeeAssignedToProject(employee_id=command.employee_id, project_id=command.project_id))
    
    
@project_module.handler(EmployeeAssignedToProject)
def on_employee_assigned_to_project(event: EmployeeAssignedToProject, logger):
    logger.info(f"Sending 'Welcome to project {event.project_id}' email to employee {event.employee_id}")
```

Keep in mind that the `employee_module` is not aware of the `project_module` and
vice versa. The only way to communicate between modules is through events.

Finally, let's put everything together:

```python
# application.py

import logging
import uuid
from lato import Application, TransactionContext
from employee_module import employee_module
from project_module import project_module
from commands import AddCandidate, HireCandidate, CreateProject, AssignEmployeeToProject, FireEmployee

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

app = Application("Modular Application", logger=logger)
app.include_submodule(project_module)
app.include_submodule(employee_module)

@app.on_enter_transaction_context
def on_enter_transaction_context(ctx: TransactionContext):
    logger = ctx[logging.Logger]
    transaction_id = uuid.uuid4()
    logger = logger.getChild(f"transaction-{transaction_id}")
    ctx.dependency_provider.update(logger=logger, transaction_id=transaction_id, publish=ctx.publish)
    logger.debug("<<< Begin transaction")

@app.on_exit_transaction_context
def on_exit_transaction_context(ctx: TransactionContext, exception=None):
    logger = ctx[logging.Logger]
    logger.debug(">>> End transaction")
    
@app.transaction_middleware
def logging_middleware(ctx: TransactionContext, call_next):
    logger = ctx[logging.Logger]
    description = f"{ctx.current_action[1]} -> {repr(ctx.current_action[0])}" if ctx.current_action else ""
    logger.debug(f"Executing {description}...")
    result = call_next()
    logger.debug(f"Finished executing {description}")
    return result


app.execute(command=AddCandidate(candidate_id="1", candidate_name="Alice"))
app.execute(command=HireCandidate(candidate_id="1"))
app.execute(command=CreateProject(project_id="1", project_name="Project 1"))
app.execute(command=AssignEmployeeToProject(employee_id="1", project_id="1"))
app.execute(command=FireEmployee(employee_id="1"))
```

The first thing to notice is that the `Application` class is instantiated with a `logger`. This logger is used as
an application level dependency. The `Application` class also provides a way to include submodules using the
`include_submodule` method. This method will automatically register all the handlers and listeners defined in the
submodule.

Next, we have the `on_enter_transaction_context` and `on_exit_transaction_context` hooks. These hooks are called
whenever a transaction context is created or destroyed. The transaction context is automatically created when
`app.execute` is called. The purpose of a transaction context is to hold all the dependencies that are required
to execute a command or handle an event, and also to create any transaction level dependencies. In this example, we
use the `on_enter_transaction_context` hook to update the transaction context with a logger and a transaction id,
but in a real application you would probably want to use the hooks to begin a database transaction and commit/rollback 
any changes. If you need to get a dependency from the transaction context, you can use the `ctx[identifier]` syntax, 
where `identifier` is the name (i.e. `logger`) or type (i.e. `logging.Logger`) of the dependency.


There is also a `logging_middleware` which is used to log the execution of any commands and events. This middleware is
automatically called whenever a command or event is executed, and there may be multiple middlewares chained together.

Finally, we have the `app.execute` calls which are used to execute commands and events. The `app.execute` method
automatically creates a transaction context and calls the `call` method of the transaction context. The `call` method
is responsible for executing the command or event, and it will automatically inject any dependencies that are required.

In addition, you can use `app.publish` to publish any external event, i.e. from a webhooks or a message queue.


## Dive deeper

For more examples check out:

- [tutorial](https://lato.readthedocs.io/en/latest/tutorial/index.html)
- [examples](https://github.com/pgorecki/lato/tree/main/examples)
- [tests](https://github.com/pgorecki/lato/tree/main/tests)


## Testing

Run the tests using pytest:

```bash
pytest tests
```


## What lato actually means?

*Lato* is the Polish word for *"summer"*. And we all know that summer is more fun than spring ;)
