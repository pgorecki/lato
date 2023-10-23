from . import project_module


@project_module.handler
def create_project_use_case(project_id, project_name, printlog):
    printlog(f"Creating project {project_name} with id {project_id}")
