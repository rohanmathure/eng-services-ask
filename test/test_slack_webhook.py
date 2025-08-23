from flask.testing import FlaskClient
import pytest


class TestSlackWebhookEndpoint:

    def test_slack_webhook_endpoint(self, test_app: FlaskClient):
        response = test_app.post("/webhooks/slack", json={"event_id": "foobar"})
        assert response.status_code == 202