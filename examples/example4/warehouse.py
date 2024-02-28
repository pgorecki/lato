from collections import defaultdict

from commands import AddItemToCart, ReceiveItemFromSupplier, RemoveItemFromCart
from pydantic import BaseModel, Field
from value_objects import CartId, ItemId, Quantity


class Stock(BaseModel):
    item_id: ItemId
    quantity: Quantity = 0
    reservations: dict[CartId, Quantity] = Field(default_factory=defaultdict)

    def move_to_cart(self, cart_id: CartId, quantity: Quantity):
        if quantity > self.quantity:
            raise ValueError("Not enough stock")
        self.quantity -= quantity
        self.reservations[cart_id] = quantity

    def return_to_stock(self, cart_id: CartId, quantity: Quantity):
        if cart_id not in self.reservations:
            raise ValueError("Not in cart")
        self.quantity += quantity
        self.reservations[cart_id] -= quantity
        if self.reservations[cart_id] == 0:
            del self.reservations[cart_id]


class StockRepository:
    ...


def receive_from_supplier(task: ReceiveItemFromSupplier, stock_repo: StockRepository):
    stock = stock_repo.get_stock(task.item_id)
    stock.quantity += task.quantity


def add_to_cart(task: AddItemToCart, stock_repo: StockRepository):
    stock = stock_repo.get_stock(task.item_id)
    stock.move_to_cart(task.cart_id, task.quantity)


def remove_from_cart(task: RemoveItemFromCart, stock_repo: StockRepository):
    stock = stock_repo.get_stock(task.item_id)
    stock.return_to_stock(task.cart_id, task.quantity)
