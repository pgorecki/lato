from application import create_ecommerce_app
from commands import AddItemToStore, GetItemDetails

from lato import compose


def test_scenario_1():
    app = create_ecommerce_app()

    app.execute(
        AddItemToStore(
            item_id="red box",
            name="Red box",
            description="A red box",
            price=10,
            quantity=100,
        )
    )

    result = compose(app.execute(GetItemDetails(item_id="red box")))

    assert result.id == "red box"


def test_scenario_2():
    app = create_ecommerce_app()

    app.execute(
        AddItemToStore(
            item_id="red box",
            name="Red box",
            description="A red box",
            price=10,
            quantity=100,
        )
    )

    result = app.execute(GetItemDetails(item_id="red box"))

    assert result is None
