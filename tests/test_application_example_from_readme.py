from uuid import uuid4

from lato import Application, TransactionContext


def test_application_example_from_readme():
    class UserService:
        def create_user(self, email, password):
            ...

    class EmailService:
        def send_welcome_email(self, email):
            ...

    app = Application(
        name="Hello World",
        # dependencies
        user_service=UserService(),
        email_service=EmailService(),
    )

    def create_user_use_case(
        email, password, session_id, ctx: TransactionContext, user_service: UserService
    ):
        # session_id, TransactionContext and UserService are automatically injected by `ctx.call`
        print("Session ID:", session_id)
        user_service.create_user(email, password)
        ctx.emit("user_created", email)

    @app.on("user_created")
    def on_user_created(email, email_service: EmailService):
        email_service.send_welcome_email(email)

    with app.transaction_context(session_id=uuid4()) as ctx:
        # session_id is transaction scoped dependency
        result = ctx.call(create_user_use_case, "alice@example.com", "password")

    assert True
