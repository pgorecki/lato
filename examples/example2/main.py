from lato import Application

app = Application()
app.include_submodule(employee_module)
app.include_submodule(project_module)
app.include_submodule(timesheet_module)
