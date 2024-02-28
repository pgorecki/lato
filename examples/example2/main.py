from employee_module import employee_module
from project import project_module

from lato import Application

app = Application()
app.include_submodule(employee_module)
app.include_submodule(project_module)
