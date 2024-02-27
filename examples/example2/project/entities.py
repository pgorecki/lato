from dataclasses import dataclass, field
from datetime import date


@dataclass
class ProjectMember:
    employee_id: str
    start_date: date
    end_date: date | None


@dataclass
class Project:
    id: str
    name: str
    members: list[ProjectMember] = field(default_factory=list)

    def has_member(self, employee_id):
        return any([m.employee_id == employee_id for m in self.members])

    def add_member(self, employee_id):
        membership = ProjectMember(
            employee_id=employee_id,
            start_date=date.today(),
            end_date=None,
        )
        self.members.append(membership)

    def remove_member(self, employee_id):
        for member in self.members[:]:
            if member.employee_id == employee_id:
                self.members.remove(member)
