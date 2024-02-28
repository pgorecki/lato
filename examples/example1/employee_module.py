from commands import AddCandidate, FireEmployee, HireCandidate
from events import CandidateHired, EmployeeFired

from lato import ApplicationModule

employee_module = ApplicationModule("employee")


@employee_module.handler(AddCandidate)
def add_candidate(task: AddCandidate, logger):
    logger.info(f"Adding candidate {task.candidate_name} with id {task.candidate_id}")


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
