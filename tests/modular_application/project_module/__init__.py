import importlib

from lato.application_module import ApplicationModule

project_module = ApplicationModule("project")
importlib.import_module(".events", __name__)
importlib.import_module(".use_cases", __name__)
