from .modular_application import create_app
from .modular_application.employee_module import add_candidate


def test_modular_application():
    app = create_app()
    app.call(add_candidate, 1, "Alice")
    assert app["logger"].history == [
        "Entering transaction",
        "Adding candidate Alice with id 1",
        "Committing transaction",
    ]


def test_get_one_handler():
    app = create_app()
    fire_employee_handlers = list(app.iterate_handlers_for("fire_employee"))

    assert len(fire_employee_handlers) == 1


def test_get_multiple_handlers():
    app = create_app()
    employee_fired_handlers = list(app.iterate_handlers_for("employee_fired"))

    assert len(employee_fired_handlers) == 2


def test_modular_application_call_by_alias():
    app = create_app()
    app.call("add_candidate", 1, "Alice")
    assert app["logger"].history == [
        "Entering transaction",
        "Adding candidate Alice with id 1",
        "Committing transaction",
    ]


def test_modular_application_emit_events():
    app = create_app()
    app.call("fire_employee", 1)
    assert app["logger"].history == [
        "Entering transaction",
        "Firing employee 1",
        "Checking if employee 1 is assigned to a project",
        "Sending exit email to 1",
        "Committing transaction",
    ]
