from events import EmployeeAssignedToProject, EmployeeFired
from tasks import AssignEmployeeToProject, CreateProject

from lato.application_module import ApplicationModule

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
    emit(
        EmployeeAssignedToProject(
            employee_id=task.employee_id, project_id=task.project_id
        )
    )


@project_module.on(EmployeeAssignedToProject)
def on_employee_assigned_to_project(event: EmployeeAssignedToProject, logger):
    logger.info(
        f"Sending 'Welcome to project {event.project_id}' email to employee {event.employee_id}"
    )
