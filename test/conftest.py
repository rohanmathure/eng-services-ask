import pytest

from project.app import create_app


@pytest.fixture(scope="class")
def test_app():
    app = create_app()
    app.testing = True
    client = app.test_client()
    yield client
