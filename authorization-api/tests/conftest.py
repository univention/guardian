import pytest

from guardian_authorization_api.logging import configure_logger


@pytest.fixture(autouse=True)
def setup_logging():
    configure_logger()
