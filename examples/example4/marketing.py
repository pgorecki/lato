from pydantic import BaseModel
from repository import Repository
from tasks import AddItemToStore, GetItemDetails, UpdateItemAttrs
from value_objects import ItemId, Money

from lato import ApplicationModule


class Item(BaseModel):
    id: ItemId
    name: str
    description: str = ""
    is_available: bool = True

    def update_main_attrs(self, name: str = None, description: str = None):
        if name:
            self.name = name
        if description:
            self.description = description

    def update_price(self, new_price: Money):
        self.price = new_price


class ItemRepository(Repository):
    ...


marketing = ApplicationModule("marketing")


@marketing.handler(AddItemToStore)
def add_item(task: AddItemToStore, item_repo: ItemRepository):
    item_repo.add(Item(id=task.item_id, name=task.name, description=task.description))


@marketing.handler(UpdateItemAttrs)
def update_attrs(task: UpdateItemAttrs, item_repo: ItemRepository):
    item = item_repo.find_by_id(task.item_id)
    item.update_main_attrs(task.name, task.description)


@marketing.handler(GetItemDetails)
def get_item_details(task: GetItemDetails, item_repo: ItemRepository):
    item = item_repo.find_by_id(task.item_id)
    return item
