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
