# Lato

## Overview
Lato is a Python microframework designed for building modular monoliths and loosely coupled applications.

## Features

- **Modularity**: Organize your application into smaller, independent modules for better maintainability.

- **Flexibility**: Loosely couple your application components, making them easier to refactor and extend.

- **Testability**: Easily test your application components in isolation.

- **Minimalistic**: Intuitive and lean API for rapid development without the bloat.


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
    ctx.emit("user_created", email)


@app.on("user_created")
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
the `project` module. When a candidate is hired, the `employee` module emits a `CandidateHired` event, which is handled
by the `employee` module to send a welcome email. When an employee is fired, the `employee` module emits an 
`EmployeeFired` event, which is handled by both the `employee` and `project` modules to send an exit email and 
to remove an employee from any projects, respectively.

First, let's start with tasks that holds all the required information to execute a use case:

```python
# tasks.py

from lato import Task


class AddCandidate(Task):
    candidate_id: str
    candidate_name: str


class HireCandidate(Task):
    candidate_id: str


class FireEmployee(Task):
    employee_id: str
    
    
class CreateProject(Task):
    project_id: str
    project_name: str
    
    
class AssignEmployeeToProject(Task):
    employee_id: str
    project_id: str
```

And the events that are emitted by the application (note that all events are expressed in past tense):

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

Now let's define the employee module. Each function which is responsible for handling a specific task is decorated
with `employee_module.handler`. Similarly, each function which is responsible for handling a specific event is
decorated with `employee_module.on`.

```python
# employee_module.py

from lato import ApplicationModule
from tasks import AddCandidate, HireCandidate, FireEmployee
from events import CandidateHired, EmployeeFired

employee_module = ApplicationModule("employee")


@employee_module.handler(AddCandidate)
def add_candidate(task: AddCandidate, logger):
    logger.info(f"Adding candidate {task.candidate_name} with id {task.candidate_id}")


@employee_module.handler(HireCandidate)
def hire_candidate(task: HireCandidate, emit, logger):
    logger.info(f"Hiring candidate {task.candidate_id}")
    emit(CandidateHired(candidate_id=task.candidate_id))


@employee_module.handler(FireEmployee)
def fire_employee(task: FireEmployee, emit, logger):
    logger.info(f"Firing employee {task.employee_id}")
    emit(EmployeeFired(employee_id=task.employee_id))


@employee_module.on(CandidateHired)
def on_candidate_hired(event: CandidateHired, logger):
    logger.info(f"Sending onboarding email to {event.candidate_id}")


@employee_module.on(EmployeeFired)
def on_employee_fired(event: EmployeeFired, logger):
    logger.info(f"Sending exit email to {event.employee_id}")
```

As you can see, some functions have additional parameters (such as `logger` or `emit`) which are automatically 
injected by the application (to be more specific, by a transaction context) upon task or event execution. This allows 
you to test your functions in isolation, without having to worry about dependencies. 

The structure of the project module is similar to the employee module:

```python
# project_module.py

from lato.application_module import ApplicationModule
from tasks import CreateProject, AssignEmployeeToProject
from events import EmployeeFired, EmployeeAssignedToProject

project_module = ApplicationModule("project")


@project_module.on(EmployeeFired)
def on_employee_fired(event: EmployeeFired, logger):
    logger.info(f"Checking if employee {event.employee_id} is assigned to a project")


@project_module.handler(CreateProject)
def create_project(task: CreateProject, logger):
    logger.info(f"Creating project {task.project_name} with id {task.project_id}")
    
    
@project_module.handler(AssignEmployeeToProject)
def assign_employee_to_project(task: AssignEmployeeToProject, emit, logger):
    logger.info(f"Assigning employee {task.employee_id} to project {task.project_id}")
    emit(EmployeeAssignedToProject(employee_id=task.employee_id, project_id=task.project_id))
    
    
@project_module.on(EmployeeAssignedToProject)
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
from tasks import AddCandidate, HireCandidate, CreateProject, AssignEmployeeToProject, FireEmployee

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
    ctx.dependency_provider.update(logger=logger, transaction_id=transaction_id, emit=ctx.emit)
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


app.execute(task=AddCandidate(candidate_id="1", candidate_name="Alice"))
app.execute(task=HireCandidate(candidate_id="1"))
app.execute(task=CreateProject(project_id="1", project_name="Project 1"))
app.execute(task=AssignEmployeeToProject(employee_id="1", project_id="1"))
app.execute(task=FireEmployee(employee_id="1"))
```

The first thing to notice is that the `Application` class is instantiated with a `logger`. This logger is used as
an application level dependency. The `Application` class also provides a way to include submodules using the
`include_submodule` method. This method will automatically register all the handlers and listeners defined in the
submodule.

Next, we have the `on_enter_transaction_context` and `on_exit_transaction_context` hooks. These hooks are called
whenever a transaction context is created or destroyed. The transaction context is automatically created when
`app.execute` is called. The purpose of a transaction context is to hold all the dependencies that are required
to execute a task or handle an event, and also to create any transaction level dependencies. In this example, we
use the `on_enter_transaction_context` hook to update the transaction context with a logger and a transaction id,
but in a real application you would probably want to use the hooks to begin a database transaction and commit/rollback 
any changes. If you need to get a dependency from the transaction context, you can use the `ctx[identifier]` syntax, 
where `identifier` is the name (i.e. `logger`) or type (i.e. `logging.Logger`) of the dependency.


There is also a `logging_middleware` which is used to log the execution of any tasks and events. This middleware is
automatically called whenever a task or event is executed, and there may be multiple middlewares chained together.

Finally, we have the `app.execute` calls which are used to execute tasks and events. The `app.execute` method
automatically creates a transaction context and calls the `call` method of the transaction context. The `call` method
is responsible for executing the task or event, and it will automatically inject any dependencies that are required.

In addition, you can use `app.emit` to emit any external event, i.e. from a webhooks or a message queue.

## Examples

Check out the [examples](https://github.com/pgorecki/lato/tree/main/examples) and 
[tests](https://github.com/pgorecki/lato/tree/main/tests) for more examples.

## Docs

Coming soon...

## Testing

Run the tests using pytest:

```bash
pytest tests
```



## What lato actually means?

*Lato* is the Polish word for *"summer"*. And we all know that summer is more fun than spring ;)