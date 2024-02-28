from dataclasses import dataclass, field
from datetime import date

from common import Repository

from lato import ApplicationModule, Command, Event, TransactionContext


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


class HireEmployee(Command):
    employee_id: int
    employee_name: str
    role: str


class FireEmployee(Command):
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

employee_module = ApplicationModule("employee")


@employee_module.handler
def hire_employee(command: HireEmployee, repository: EmployeeRepository):
    employee = Employee(id=command.employee_id, name=command.employee_name)
    employee.add_engagement(WorkEngagement(command.role, date.today()))
    repository.add(employee)


@employee_module.handler
def fire_employee(
    command: FireEmployee, repository: EmployeeRepository, ctx: TransactionContext
):
    employee = repository.get(command.employee_id)
    employee.end_current_engagement()
    ctx.publish(EmployeeWasFired(employee_id=employee.id))
