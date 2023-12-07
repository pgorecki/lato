from lato.testing import override

from .sample_application import sample_use_case


class FakeFooService:
    def run(self):
        return "Running FakeFooService"


class FakeBarService:
    def run(self):
        return "Running FakeBarService"


def test_sample_application_with_real_services(sample_application):
    result = sample_application.call(sample_use_case)
    assert result == "Running RealFooService, Running RealBarService"


def test_sample_application_with_foo_override(sample_application):
    with override(sample_application, foo_service=FakeFooService()) as overridden:
        result = overridden.call(sample_use_case)
        assert result == "Running FakeFooService, Running RealBarService"


def test_sample_application_with_bar_override(sample_application):
    with override(sample_application, bar_service=FakeBarService()) as overridden:
        result = overridden.call(sample_use_case)
        assert result == "Running RealFooService, Running FakeBarService"


def test_overridding_reset(sample_application):
    original_foo_service = sample_application["foo_service"]
    with override(sample_application, foo_service=FakeFooService()) as overridden:
        assert isinstance(sample_application["foo_service"], FakeFooService)
    assert sample_application["foo_service"] == original_foo_service
