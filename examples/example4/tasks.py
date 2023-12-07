from value_objects import CartId, ItemId, Money, Quantity

from lato import Task

# queries


class GetItemDetails(Task):
    item_id: ItemId


# commands


class AddItemToCart(Task):
    cart_id: CartId
    item_id: ItemId
    quantity: Quantity


class RemoveItemFromCart(Task):
    cart_id: CartId
    item_id: ItemId
    quantity: Quantity


class UpdateItemPrice(Task):
    item_id: ItemId
    price: Money


class AddItemToStore(Task):
    item_id: ItemId
    name: str
    description: str = None
    price: Money
    quantity: Quantity


class UpdateItemAttrs(Task):
    item_id: ItemId
    name: str = None
    description: str = None


class ReceiveItemFromSupplier(Task):
    item_id: ItemId
    quantity: Quantity
