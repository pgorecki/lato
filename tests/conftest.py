import pytest

from tests.sample_application import application


@pytest.fixture
def sample_application():
    return application
