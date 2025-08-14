import pytest

from app import app as create_app


@pytest.fixture
def test_app():
    app = create_app()
    yield app
    app.teardown()
