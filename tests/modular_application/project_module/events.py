from . import project_module


@project_module.on("employee_fired")
def on_employee_fired(employee_id, printlog):
    printlog(f"Checking if employee {employee_id} is assigned to a project")
