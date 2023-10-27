from events import CandidateHired, EmployeeFired
from tasks import AddCandidate, FireEmployee, HireCandidate

from lato import ApplicationModule

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
