from lato import Application, TransactionContext, Event
from lato.dependency_provider import SimpleDependencyProvider


class RealFooService:
    def run(self):
        return "Running RealFooService"


class RealBarService:
    def run(self):
        return "Running RealBarService"


def sample_use_case(foo_service, bar_service):
    return ", ".join([foo_service.run(), bar_service.run()])


dependency_provider = SimpleDependencyProvider(
    foo_service=RealFooService(),
)

application = Application("sample_application", dependency_provider=dependency_provider)


@application.on_create_transaction_context
def on_create_transaction_context():
    dependency_provider = SimpleDependencyProvider(
        foo_service=application["foo_service"],  # same dependency for each transaction
        bar_service=RealBarService(),  # new dependency for each transaction
    )
    return TransactionContext(dependency_provider=dependency_provider)
