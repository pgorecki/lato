from lato import ApplicationModule

employee_module = ApplicationModule("employee")


@employee_module.handler
def add_candidate(candidate_id, name, printlog):
    printlog(f"Adding candidate {name} with id {candidate_id}")


@employee_module.handler
def hire_candidate(candidate_id, emit, printlog):
    printlog(f"Hiring candidate {candidate_id}")
    emit("candidate_hired", candidate_id)


@employee_module.handler
def fire_employee(employee_id, emit, printlog):
    printlog(f"Firing employee {employee_id}")
    emit("employee_fired", employee_id)


@employee_module.on("employee_hired")
def on_employee_hired(employee_id, printlog):
    printlog(f"Sending onboarding email to {employee_id}")


@employee_module.on("employee_fired")
def on_employee_fired(employee_id, printlog):
    printlog(f"Sending exit email to {employee_id}")
