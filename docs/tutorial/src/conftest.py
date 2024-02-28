import pytest
from application import create_app


@pytest.fixture
def app():
    return create_app()
