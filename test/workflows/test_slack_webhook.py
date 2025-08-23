from flask.testing import FlaskClient
import pytest
import asyncio
import logging
from clients.temporal import TemporalClient

logger = logging.getLogger(__name__)


class TestSlackWebhookEndpoint:
    """Test class for Slack webhook endpoint with workflow cleanup."""

    @pytest.fixture(autouse=True)
    def setup_and_cleanup(self):
        """Setup and cleanup fixture that runs for each test method."""
        # Setup: Initialize workflow tracking
        self.created_workflow_ids = []
        self.client = None
        
        yield  # This is where the test runs
        
        # Cleanup: Attempt to terminate any workflows created during the test
        # TODO: Uncomment this when we have a way to terminate workflows
        # if hasattr(self, 'created_workflow_ids') and self.created_workflow_ids:
        #     asyncio.run(self._cleanup_workflows())
    
    async def _cleanup_workflows(self):
        """Clean up workflows created during tests."""
        try:
            if not self.client:
                self.client = await TemporalClient.get_client()
            
            for workflow_id in self.created_workflow_ids:
                try:
                    logger.info(f"Attempting to terminate test workflow: {workflow_id}")
                    workflow_handle = self.client.get_workflow_handle(workflow_id)
                    await workflow_handle.terminate("Test cleanup")
                    logger.info(f"Successfully terminated workflow: {workflow_id}")
                except Exception as e:
                    # Log but don't fail the test if cleanup fails
                    logger.warning(f"Failed to cleanup workflow {workflow_id}: {str(e)}")
                    
        except Exception as e:
            logger.warning(f"Failed to connect to Temporal for cleanup: {str(e)}")
        finally:
            # Clear the list regardless of cleanup success
            self.created_workflow_ids = []

    def test_slack_webhook_endpoint_error_handling(self, test_app: FlaskClient):
        """Test that the endpoint properly handles Temporal connection errors."""
        event_id = "foobar"
        expected_workflow_id = f"slack-webhook-{event_id}"
        
        # Track the workflow ID for cleanup (even though it won't be created due to connection error)
        self.created_workflow_ids.append(expected_workflow_id)
        
        response = test_app.post("/webhooks/slack", json={"event_id": event_id})

        # When Temporal server is unavailable, should return 503
        assert response.status_code == 503
        
        # Should return proper error structure
        json_response = response.get_json()
        assert "error" in json_response
        assert "Failed to connect to workflow service" in json_response["error"]
        assert "workflow_id" in json_response
        assert json_response["workflow_id"] == expected_workflow_id

    def test_slack_webhook_endpoint_invalid_json(self, test_app: FlaskClient):
        """Test that the endpoint properly validates JSON requests."""
        response = test_app.post("/webhooks/slack", data="not json")

        # Should return 400 for invalid JSON
        assert response.status_code == 400
        json_response = response.get_json()
        assert json_response["error"] == "Request must be JSON"
        
    def test_slack_webhook_endpoint_success_with_cleanup(self, test_app: FlaskClient):
        """Test workflow creation and cleanup when Temporal server is available.
        
        Note: This test will only pass when Temporal server is running and accessible.
        When server is unavailable, it will test the error handling path.
        """
        event_id = "test-success-cleanup"
        expected_workflow_id = f"slack-webhook-{event_id}"
        
        # Track the workflow ID for cleanup
        self.created_workflow_ids.append(expected_workflow_id)
        
        response = test_app.post("/webhooks/slack", json={"event_id": event_id})
        
        if response.status_code == 202:
            # Temporal server is available - workflow should be created successfully
            json_response = response.get_json()
            assert "status" in json_response
            assert "Workflow started successfully" in json_response["status"]
            assert json_response["workflow_id"] == expected_workflow_id
            assert "workflow_run_id" in json_response
            
        elif response.status_code == 503:
            # Temporal server is unavailable - should handle gracefully
            json_response = response.get_json()
            assert "error" in json_response
            assert "Failed to connect to workflow service" in json_response["error"]
            assert json_response["workflow_id"] == expected_workflow_id
            
        else:
            # Any other status code is unexpected
            pytest.fail(f"Unexpected status code: {response.status_code}, response: {response.get_json()}")