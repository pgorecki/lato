from lato import Event


class CandidateHired(Event):
    candidate_id: str


class EmployeeFired(Event):
    employee_id: str


class EmployeeAssignedToProject(Event):
    employee_id: str
    project_id: str
