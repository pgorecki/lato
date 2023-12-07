Shopping cart:
- add items (name, price, quantity)
- remove items
- save for later (move to wishlist)
- show total price

Law does not allow us to change the price of an item once it is added to the cart.

I also want to show users how many items are left in stock (known by warehouse). 
But when users add items, there is constant flow of interactions between the cart and the warehouse.

When price is changing, then update the price, remove from shopping cart, move to wishlist. Show
current price and last price.

Marketing copy name and description to shopping cart.


Copuling - one part of the domain trying to issue a command to other part of the domain.



Sales - prices, current, last, history, logically responsible for the concept of a shopping cart (cart id)
list of (item id, price history)


Warehouse - availability, quantity

Shipping - est. delivery

Marketing - description


composition gateway

decomposition gateway

notify users of 1 week stale carts

wipe 1 month stale carts