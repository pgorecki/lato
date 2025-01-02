from lato import Application, ApplicationModule, Command


class GetAllItemDetails(Command):
    pass


pricing_module = ApplicationModule("pricing")


@pricing_module.handler(GetAllItemDetails)
def get_item_price(command: GetAllItemDetails):
    prices = {"pencil": 1, "pen": 2}
    return prices


warehouse_module = ApplicationModule("warehouse")


@warehouse_module.handler(GetAllItemDetails)
def get_item_stock(command: GetAllItemDetails):
    stocks = {"pencil": 100, "pen": 80}
    return stocks


app = Application()
app.include_submodule(pricing_module)
app.include_submodule(warehouse_module)


@app.compose(GetAllItemDetails)
def compose_item_details(pricing, warehouse):
    assert pricing == {"pencil": 1, "pen": 2}
    assert warehouse == {"pencil": 100, "pen": 80}

    details = [
        dict(item_id=x, price=pricing[x], stock=warehouse[x]) for x in pricing.keys()
    ]
    return details


assert app.execute(GetAllItemDetails()) == [
    {"item_id": "pencil", "price": 1, "stock": 100},
    {"item_id": "pen", "price": 2, "stock": 80},
]
