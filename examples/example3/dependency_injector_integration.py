import copy
import inspect
import uuid
from typing import Optional

from dependency_injector import containers, providers
from dependency_injector.containers import Container
from dependency_injector.providers import Dependency, Factory, Provider, Singleton
from dependency_injector.wiring import Provide, inject  # noqa

from lato import Application, DependencyProvider, TransactionContext


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


class ApplicationContainer(containers.DeclarativeContainer):
    name = providers.Object("Foo")
    engine = providers.Singleton(Engine, "sqlite:///:memory:")


class TransactionContainer(containers.DeclarativeContainer):
    correlation_id = providers.Dependency(instance_of=uuid.UUID)
    session = providers.Dependency(instance_of=Session)
    repository = providers.Singleton(Repository, session=session)


def resolve_provider_by_type(container: Container, cls: type) -> Optional[Provider]:
    def inspect_provider(provider: Provider) -> bool:
        if isinstance(provider, (Factory, Singleton)):
            return issubclass(provider.cls, cls)
        elif isinstance(provider, Dependency):
            return issubclass(provider.instance_of, cls)

        return False

    matching_providers = inspect.getmembers(
        container,
        inspect_provider,
    )
    if matching_providers:
        if len(matching_providers) > 1:
            raise ValueError(
                f"Cannot uniquely resolve {cls}. Found {len(providers)} matching providers."
            )
        return matching_providers[0][1]
    return None


class ContainerProvider(DependencyProvider):
    def __init__(self, container: Container):
        self.container = container
        self.counter = 0

    def has_dependency(self, identifier: str | type) -> bool:
        if isinstance(identifier, type) and resolve_provider_by_type(
            self.container, identifier
        ):
            return True
        if type(identifier) is str:
            return identifier in self.container.providers

    def register_dependency(self, identifier, dependency_instance):
        pr = providers.Object(dependency_instance)
        try:
            setattr(self.container, identifier, pr)
        except TypeError:
            setattr(self.container, f"{str(identifier)}-{self.counter}", pr)
            self.counter += 1

    def get_dependency(self, identifier):
        try:
            if isinstance(identifier, type):
                provider = resolve_provider_by_type(self.container, identifier)
            else:
                provider = getattr(self.container, identifier)
            instance = provider()
        except Exception as e:
            raise e
        return instance

    def copy(self, *args, **kwargs):
        dp = ContainerProvider(copy.copy(self.container))
        dp.update(*args, **kwargs)
        return dp


# some tests...
ac = ApplicationContainer()

dp1 = ContainerProvider(ac)

# make a copy
dp2 = dp1.copy()

# make sure that the original and the copy are the same
assert dp1["name"] == dp2["name"] == "Foo"
assert dp1["engine"] is dp2["engine"]

# create a copy with overriden value
dp3 = dp1.copy(name="Bar")

# make sure that the original was not overriden
assert dp3["name"] == "Bar" and dp1["name"] == "Foo"


app = Application(dependency_provider=ContainerProvider(ApplicationContainer()))


@app.on_create_transaction_context
def on_create_transaction_context():
    # if you want to share application container with transaction context use this:
    # return TransactionContext(app.dependency_provider)

    # if you want to have a separate container for transaction context use this:
    engine = app.dependency_provider["engine"]
    dp = ContainerProvider(
        TransactionContainer(
            correlation_id=uuid.uuid4(), session=engine.create_sesson()
        )
    )
    return TransactionContext(dp)


@app.on_enter_transaction_context
def on_enter_transaction_context(ctx: TransactionContext):
    print("New transaction started")


def foo(correlation_id: uuid.UUID, session: Session, repository: Repository):
    print(correlation_id, session, repository)


with app.transaction_context() as ctx:
    ctx.call(foo)
    ctx.call(foo)

with app.transaction_context() as ctx:
    ctx.call(foo)
