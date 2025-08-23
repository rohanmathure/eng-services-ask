from flask.testing import FlaskClient
import pytest


class TestSlackWebhookEndpoint:

    def test_slack_webhook_endpoint_error_handling(self, test_app: FlaskClient):
        """Test that the endpoint properly handles Temporal connection errors."""
        response = test_app.post("/webhooks/slack", json={"event_id": "foobar"})

        # When Temporal server is unavailable, should return 503
        assert response.status_code == 503
        
        # Should return proper error structure
        json_response = response.get_json()
        assert "error" in json_response
        assert "Failed to connect to workflow service" in json_response["error"]
        assert "workflow_id" in json_response
        assert json_response["workflow_id"] == "slack-webhook-foobar"

    def test_slack_webhook_endpoint_invalid_json(self, test_app: FlaskClient):
        """Test that the endpoint properly validates JSON requests."""
        response = test_app.post("/webhooks/slack", data="not json")

        # Should return 400 for invalid JSON
        assert response.status_code == 400
        json_response = response.get_json()
        assert json_response["error"] == "Request must be JSON"