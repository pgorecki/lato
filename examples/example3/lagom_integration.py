import uuid

import lagom.exceptions
from lagom import Container

from lato import Application, DependencyProvider, TransactionContext
from lato.dependency_provider import as_type


class CorrelationId(uuid.UUID):
    pass


class Name(str):
    pass


class Session:
    ...


class Repository:
    def __init__(self, session: Session):
        self.session = session


class Engine:
    def __init__(self, url):
        self.url = url

    def create_sesson(self):
        return Session()


application_container = Container()
application_container[Name] = "Foo"
application_container[Engine] = Engine("sqlite:///:memory:")


class LagomDependencyProvider(DependencyProvider):
    allow_names = False

    def __init__(self, lagom_container):
        self.container = lagom_container

    def has_dependency(self, identifier: str | type) -> bool:
        if type(identifier) is str:
            return False
        return identifier in self.container.defined_types

    def register_dependency(self, identifier, dependency):
        if type(identifier) is str:
            raise ValueError(
                f"Lagom container does not support string identifiers: {identifier}"
            )
        try:
            self.container[identifier] = dependency
        except lagom.exceptions.DuplicateDefinition:
            pass

    def get_dependency(self, identifier):
        if type(identifier) is str:
            raise ValueError(
                f"Lagom container does not support string identifiers: {identifier}"
            )
        return self.container[identifier]

    def copy(self, *args, **kwargs) -> DependencyProvider:
        dp = LagomDependencyProvider(self.container.clone())
        dp.update(*args, **kwargs)
        return dp


dp1 = LagomDependencyProvider(application_container)

# make a copy
dp2 = dp1.copy()

# make sure that the original and the copy are the same
assert dp1[Name] == dp2[Name] == "Foo"
assert dp1[Engine] is dp2[Engine]

# create a copy with overriden value
dp3 = dp1.copy(name=as_type("Bar", Name))  # not yet implemented

# make sure that the original was not overriden
assert dp3[Name] == "Bar" and dp1[Name] == "Foo"


app = Application(dependency_provider=LagomDependencyProvider(application_container))


@app.on_create_transaction_context
def on_create_transaction_context():
    # if you want to share application container with transaction context use this:
    # return TransactionContext(app.dependency_provider)

    # if you want to have a separate container for transaction context use this:
    engine = app.dependency_provider[Engine]
    transaction_container = Container()
    transaction_container[CorrelationId] = uuid.uuid4()
    transaction_container[Session] = engine.create_sesson()
    transaction_container[Repository] = Repository(transaction_container[Session])
    dp = LagomDependencyProvider(transaction_container)
    return TransactionContext(dp)


@app.on_enter_transaction_context
def on_enter_transaction_context(ctx: TransactionContext):
    print("New transaction started", ctx)


def foo(correlation_id: CorrelationId, session: Session, repository: Repository):
    print(correlation_id, session, repository)


with app.transaction_context() as ctx:
    ctx.call(foo)
    ctx.call(foo)

with app.transaction_context() as ctx:
    ctx.call(foo)
