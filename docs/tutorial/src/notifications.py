from events import TodoWasCompleted
from queries import GetTodoDetails
from todos import TodoReadModel

from lato import ApplicationModule, TransactionContext


class NotificationService:
    def push(self, message):
        print(message)


notifications = ApplicationModule("notifications")


@notifications.handler(TodoWasCompleted)
def on_todo_was_completed(
    event: TodoWasCompleted, service: NotificationService, ctx: TransactionContext
):
    details: TodoReadModel = ctx.execute(GetTodoDetails(todo_id=event.todo_id))
    print(details)
    message = f"A todo {details.title} was completed"
    service.push(message)
