from dataclasses import dataclass, field
from datetime import date

from common import Repository

from lato import ApplicationModule, Event, Task, TransactionContext


@dataclass
class WorkEngagement:
    role: str
    start_date: date
    end_date: date = None


@dataclass
class Employee:
    id: int
    name: str
    engagements: list[WorkEngagement] = field(default_factory=list)

    def add_engagement(self, engagement: WorkEngagement):
        self.engagements.append(engagement)

    def end_current_engagement(self):
        self.engagements[-1].end_date = date.today()

    def get_current_role(self):
        return self.engagements[-1].role

    def __hash__(self):
        return hash(self.id)


class HireEmployee(Task):
    employee_id: int
    employee_name: str
    role: str


class FireEmployee(Task):
    employee_id: int


class EmployeeWasFired(Event):
    employee_id: str


class EmployeeRepository(Repository):
    pass


# arrange module

employee_repository = EmployeeRepository()

employee1 = Employee(1, "Alice")
employee2 = Employee(2, "Bob")
employee_repository.add(employee1)
employee_repository.add(employee2)

employee_module = ApplicationModule("employee", employee_repository)


@employee_module.handler
def hire_employee(task: HireEmployee, repository: EmployeeRepository):
    employee = Employee(id=task.employee_id, name=task.employee_name)
    employee.add_engagement(WorkEngagement(task.role, date.today()))
    repository.add(employee)


@employee_module.handler
def fire_employee(
    task: FireEmployee, repository: EmployeeRepository, ctx: TransactionContext
):
    employee = repository.get(task.employee_id)
    employee.end_current_engagement()
    ctx.emit(EmployeeWasFired(employee_id=employee.id))
