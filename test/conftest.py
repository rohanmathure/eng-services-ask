import pytest
import os

from dotenv import dotenv_values
from project.app import create_app

config = {
    **dotenv_values(".env.shared"),  # load shared development variables
    **dotenv_values(".env.secret"),  # load sensitive variables
    **os.environ,  # override loaded values with environment variables
}

@pytest.fixture(scope="class")
def test_app():
    # Apply environment variables from dotenv
    for key, value in config.items():
        if key and value is not None:
            os.environ[key] = str(value)
    
    app = create_app()
    app.testing = True
    client = app.test_client()
    yield client


