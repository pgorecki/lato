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
