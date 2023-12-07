from marketing import ItemRepository as MarketingItemRepository
from marketing import marketing
from repository import InMemoryRepository
from sales import CartRepository as SalesCartRepository
from sales import ItemRepository as SalesItemRepository
from sales import sales

from lato import Application, as_type

# from warehouse import warehouse


def create_ecommerce_app():
    ecommerce = Application(
        "ecommerce",
        item_repo=as_type(InMemoryRepository(), MarketingItemRepository),
    )
    ecommerce.dependency_provider.update(
        as_type(InMemoryRepository(), MarketingItemRepository),
        as_type(InMemoryRepository(), SalesItemRepository),
        as_type(InMemoryRepository(), SalesCartRepository),
    )
    ecommerce.include_submodule(marketing)
    ecommerce.include_submodule(sales)
    # ecommerce.include_submodule(warehouse)

    return ecommerce
