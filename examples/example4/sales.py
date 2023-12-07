from pydantic import BaseModel, Field
from repository import Repository
from tasks import AddItemToCart, RemoveItemFromCart, UpdateItemPrice
from value_objects import CartId, ItemId, Money, Quantity

from lato import ApplicationModule

# domain models


class Item(BaseModel):
    item_id: ItemId
    price: Money

    def update_price(self, new_price: Money):
        self.price = new_price


class CartItem(BaseModel):
    item_id: ItemId
    current_price: Money
    last_price: Money
    quantity: Quantity


class Cart(BaseModel):
    id: CartId
    items: set[CartItem] = Field(default_factory=set)

    def get_item(self, item_id: ItemId):
        for item in self.items:
            if item.item_id == item_id:
                return item
        return CartItem(item_id=item_id, quantity=0, current_price=0, last_price=0)

    def add_item(self, item_id: ItemId, quantity: Quantity, price: Money):
        current = self.get_item(item_id)
        updated = CartItem(
            item_id=item_id,
            quantity=current.quantity + quantity,
            current_price=price,
            last_price=price,
        )
        self.items.remove(current)
        self.items.add(updated)

    def remove_item(self, item_id: ItemId, quantity: Quantity):
        for item in self.items:
            if item.item_id == item_id:
                item.quantity -= quantity
                if item.quantity == 0:
                    self.items.remove(item)
                return
        raise ValueError("Item not in cart")


class CartRepository(Repository):
    ...


class ItemRepository(Repository):
    ...


sales = ApplicationModule("sales")


@sales.handler(UpdateItemPrice)
def update_price(task: UpdateItemPrice, item_repo: ItemRepository):
    item = item_repo.find_by_id(task.item_id)
    item.update_price(task.price)


@sales.handler(AddItemToCart)
def add_item_to_cart(
    task: AddItemToCart, item_repo: ItemRepository, cart_repo: CartRepository
):
    item = item_repo.find_by_id(task.item_id)
    cart = cart_repo.find_by_id(task.cart_id)
    cart.add_item(task.item_id, task.quantity, item.price)
    # send 1 week timeout to remind
    # send 1 month timeout to wipe cart


@sales.handler(RemoveItemFromCart)
def remove_from_cart(task: RemoveItemFromCart, cart_repo: CartRepository):
    cart = cart_repo.find_by_id(task.cart_id)
    cart.remove_item(task.item_id, task.quantity)
