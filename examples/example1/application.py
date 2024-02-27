import logging
import uuid

from employee_module import employee_module
from project_module import project_module
from commands import (
    AddCandidate,
    AssignEmployeeToProject,
    CreateProject,
    FireEmployee,
    HireCandidate,
)

from lato import Application, TransactionContext

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

app = Application("Modular Application", logger=logger)
app.include_submodule(project_module)
app.include_submodule(employee_module)


@app.on_enter_transaction_context
def on_enter_transaction_context(ctx: TransactionContext):
    app_logger = app.get_dependency('logger')
    transaction_id = uuid.uuid4()
    ctx_logger = app_logger.getChild(f"transaction-{transaction_id}")
    ctx.set_dependencies(
        logger=ctx_logger, transaction_id=transaction_id, publish=ctx.publish
    )
    logger.debug("<<< Begin transaction")


@app.on_exit_transaction_context
def on_exit_transaction_context(ctx: TransactionContext, exception=None):
    logger = ctx[logging.Logger]
    logger.debug(">>> End transaction")


@app.transaction_middleware
def logging_middleware(ctx: TransactionContext, call_next):
    logger = ctx[logging.Logger]
    description = (
        f"{ctx.current_action[1]} -> {repr(ctx.current_action[0])}"
        if ctx.current_action
        else ""
    )
    logger.debug(f"Executing {description}...")
    result = call_next()
    logger.debug(f"Finished executing {description}")
    return result


app.execute(AddCandidate(candidate_id="1", candidate_name="Alice"))
app.execute(HireCandidate(candidate_id="1"))
app.execute(CreateProject(project_id="1", project_name="Project 1"))
app.execute(AssignEmployeeToProject(employee_id="1", project_id="1"))
app.execute(FireEmployee(employee_id="1"))
