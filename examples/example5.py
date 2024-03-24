from lato import Application, ApplicationModule, Command


class GetItemDetails(Command):
    item_id: str


pricing_module = ApplicationModule("pricing")


@pricing_module.handler(GetItemDetails)
def get_item_price(command: GetItemDetails):
    prices = {"pencil": 1, "pen": 2}
    return {"price": prices[command.item_id]}


warehouse_module = ApplicationModule("warehouse")


@warehouse_module.handler(GetItemDetails)
def get_item_stock(command: GetItemDetails):
    stocks = {"pencil": 100, "pen": 80}
    return {"stock": stocks[command.item_id]}


app = Application()
app.include_submodule(pricing_module)
app.include_submodule(warehouse_module)

assert app.execute(GetItemDetails(item_id="pen")) == {"price": 2, "stock": 80}
