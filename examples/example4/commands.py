from value_objects import CartId, ItemId, Money, Quantity

from lato import Command

# queries


class GetItemDetails(Command):
    item_id: ItemId


# commands


class AddItemToCart(Command):
    cart_id: CartId
    item_id: ItemId
    quantity: Quantity


class RemoveItemFromCart(Command):
    cart_id: CartId
    item_id: ItemId
    quantity: Quantity


class UpdateItemPrice(Command):
    item_id: ItemId
    price: Money


class AddItemToStore(Command):
    item_id: ItemId
    name: str
    description: str = None
    price: Money
    quantity: Quantity


class UpdateItemAttrs(Command):
    item_id: ItemId
    name: str = None
    description: str = None


class ReceiveItemFromSupplier(Command):
    item_id: ItemId
    quantity: Quantity
