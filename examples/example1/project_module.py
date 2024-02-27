from events import EmployeeAssignedToProject, EmployeeFired
from commands import AssignEmployeeToProject, CreateProject

from lato.application_module import ApplicationModule

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
    publish(
        EmployeeAssignedToProject(
            employee_id=command.employee_id, project_id=command.project_id
        )
    )


@project_module.handler(EmployeeAssignedToProject)
def on_employee_assigned_to_project(event: EmployeeAssignedToProject, logger):
    logger.info(
        f"Sending 'Welcome to project {event.project_id}' email to employee {event.employee_id}"
    )
