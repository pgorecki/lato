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
any changes.

There is also a `logging_middleware` which is used to log the execution of any tasks and events. This middleware is
automatically called whenever a task or event is executed, and there may be multiple middlewares chained together.

Finally, we have the `app.execute` calls which are used to execute tasks and events. The `app.execute` method
automatically creates a transaction context and calls the `call` method of the transaction context. The `call` method
is responsible for executing the task or event, and it will automatically inject any dependencies that are required.

In addition, you can use `app.emit` to emit any external event, i.e. from a webhooks or a message queue. 

If executed, the application will produce the following log:

```
transaction-7d913a29-e3ca-4046-82bd-3bf48e448d29 - DEBUG - <<< Begin transaction
transaction-7d913a29-e3ca-4046-82bd-3bf48e448d29 - DEBUG - Executing <function add_candidate at 0x7f68dc206dd0> -> AddCandidate(task_id=UUID('993c5675-da59-4b83-a948-486cef1a9509'), candidate_id='1', candidate_name='Alice')...
transaction-7d913a29-e3ca-4046-82bd-3bf48e448d29 - INFO - Adding candidate Alice with id 1
transaction-7d913a29-e3ca-4046-82bd-3bf48e448d29 - DEBUG - Finished executing <function add_candidate at 0x7f68dc206dd0> -> AddCandidate(task_id=UUID('993c5675-da59-4b83-a948-486cef1a9509'), candidate_id='1', candidate_name='Alice')
transaction-7d913a29-e3ca-4046-82bd-3bf48e448d29 - DEBUG - >>> End transaction
transaction-b4554a80-b86d-40be-9b96-c395a2dd46d0 - DEBUG - <<< Begin transaction
transaction-b4554a80-b86d-40be-9b96-c395a2dd46d0 - DEBUG - Executing <function hire_candidate at 0x7f68dc1cd480> -> HireCandidate(task_id=UUID('9a019495-637e-4aa1-a6ed-77294403e05d'), candidate_id='1')...
transaction-b4554a80-b86d-40be-9b96-c395a2dd46d0 - INFO - Hiring candidate 1
transaction-b4554a80-b86d-40be-9b96-c395a2dd46d0 - DEBUG - Executing <function on_candidate_hired at 0x7f68dc1cd5a0> -> CandidateHired(event_id=UUID('9dfc45d3-86c1-4405-aef0-3367272d23d8'), candidate_id='1')...
transaction-b4554a80-b86d-40be-9b96-c395a2dd46d0 - INFO - ** Sending onboarding email to 1
transaction-b4554a80-b86d-40be-9b96-c395a2dd46d0 - DEBUG - Finished executing <function on_candidate_hired at 0x7f68dc1cd5a0> -> CandidateHired(event_id=UUID('9dfc45d3-86c1-4405-aef0-3367272d23d8'), candidate_id='1')
transaction-b4554a80-b86d-40be-9b96-c395a2dd46d0 - DEBUG - Finished executing <function hire_candidate at 0x7f68dc1cd480> -> HireCandidate(task_id=UUID('9a019495-637e-4aa1-a6ed-77294403e05d'), candidate_id='1')
transaction-b4554a80-b86d-40be-9b96-c395a2dd46d0 - DEBUG - >>> End transaction
transaction-2420052e-354a-42cf-a9db-9654e1aaaf28 - DEBUG - <<< Begin transaction
transaction-2420052e-354a-42cf-a9db-9654e1aaaf28 - DEBUG - Executing <function create_project at 0x7f68dc1cd7e0> -> CreateProject(task_id=UUID('eb2aa32a-c5d7-429e-a26e-f4ac7e430149'), project_id='1', project_name='Project 1')...
transaction-2420052e-354a-42cf-a9db-9654e1aaaf28 - INFO - Creating project Project 1 with id 1
transaction-2420052e-354a-42cf-a9db-9654e1aaaf28 - DEBUG - Finished executing <function create_project at 0x7f68dc1cd7e0> -> CreateProject(task_id=UUID('eb2aa32a-c5d7-429e-a26e-f4ac7e430149'), project_id='1', project_name='Project 1')
transaction-2420052e-354a-42cf-a9db-9654e1aaaf28 - DEBUG - >>> End transaction
transaction-d3fc6fa7-1b3c-4872-bee2-ca597688e919 - DEBUG - <<< Begin transaction
transaction-d3fc6fa7-1b3c-4872-bee2-ca597688e919 - DEBUG - Executing <function assign_employee_to_project at 0x7f68dc1cd870> -> AssignEmployeeToProject(task_id=UUID('a2f9d016-d5a4-4d70-8642-f4906d371ab5'), employee_id='1', project_id='1')...
transaction-d3fc6fa7-1b3c-4872-bee2-ca597688e919 - INFO - Assigning employee 1 to project 1
transaction-d3fc6fa7-1b3c-4872-bee2-ca597688e919 - DEBUG - Executing <function on_employee_assigned_to_project at 0x7f68dc1cd900> -> EmployeeAssignedToProject(event_id=UUID('30d625c7-c5d6-425e-8592-093ef5e3f39a'), employee_id='1', project_id='1')...
transaction-d3fc6fa7-1b3c-4872-bee2-ca597688e919 - INFO - Sending 'Welcome to project 1' email to employee 1
transaction-d3fc6fa7-1b3c-4872-bee2-ca597688e919 - DEBUG - Finished executing <function on_employee_assigned_to_project at 0x7f68dc1cd900> -> EmployeeAssignedToProject(event_id=UUID('30d625c7-c5d6-425e-8592-093ef5e3f39a'), employee_id='1', project_id='1')
transaction-d3fc6fa7-1b3c-4872-bee2-ca597688e919 - DEBUG - Finished executing <function assign_employee_to_project at 0x7f68dc1cd870> -> AssignEmployeeToProject(task_id=UUID('a2f9d016-d5a4-4d70-8642-f4906d371ab5'), employee_id='1', project_id='1')
transaction-d3fc6fa7-1b3c-4872-bee2-ca597688e919 - DEBUG - >>> End transaction
transaction-35530dda-b233-4b0d-a061-5c69f6173451 - DEBUG - <<< Begin transaction
transaction-35530dda-b233-4b0d-a061-5c69f6173451 - DEBUG - Executing <function fire_employee at 0x7f68dc1cd510> -> FireEmployee(task_id=UUID('72d48e38-57ca-4233-a987-088f484b7fe0'), employee_id='1')...
transaction-35530dda-b233-4b0d-a061-5c69f6173451 - INFO - Firing employee 1
transaction-35530dda-b233-4b0d-a061-5c69f6173451 - DEBUG - Executing <function on_employee_fired at 0x7f68dc1cd750> -> EmployeeFired(event_id=UUID('73ef555b-3356-40d3-bb6b-168203c311ee'), employee_id='1')...
transaction-35530dda-b233-4b0d-a061-5c69f6173451 - INFO - Checking if employee 1 is assigned to a project
transaction-35530dda-b233-4b0d-a061-5c69f6173451 - DEBUG - Finished executing <function on_employee_fired at 0x7f68dc1cd750> -> EmployeeFired(event_id=UUID('73ef555b-3356-40d3-bb6b-168203c311ee'), employee_id='1')
transaction-35530dda-b233-4b0d-a061-5c69f6173451 - DEBUG - Executing <function on_employee_fired at 0x7f68dc1cd630> -> EmployeeFired(event_id=UUID('73ef555b-3356-40d3-bb6b-168203c311ee'), employee_id='1')...
transaction-35530dda-b233-4b0d-a061-5c69f6173451 - INFO - ** Sending exit email to 1
transaction-35530dda-b233-4b0d-a061-5c69f6173451 - DEBUG - Finished executing <function on_employee_fired at 0x7f68dc1cd630> -> EmployeeFired(event_id=UUID('73ef555b-3356-40d3-bb6b-168203c311ee'), employee_id='1')
transaction-35530dda-b233-4b0d-a061-5c69f6173451 - DEBUG - Finished executing <function fire_employee at 0x7f68dc1cd510> -> FireEmployee(task_id=UUID('72d48e38-57ca-4233-a987-088f484b7fe0'), employee_id='1')
transaction-35530dda-b233-4b0d-a061-5c69f6173451 - DEBUG - >>> End transaction
```