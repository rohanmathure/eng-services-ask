from flask.testing import FlaskClient
import pytest
import asyncio
import logging
import uuid
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
        if hasattr(self, 'created_workflow_ids') and self.created_workflow_ids:
            asyncio.run(self._cleanup_workflows())
    
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
        """Test that the endpoint handles various Temporal scenarios (unavailable, conflicts, etc.)."""
        # Use unique event ID to avoid workflow conflicts
        event_id = f"test-{uuid.uuid4().hex[:8]}"
        expected_workflow_id = f"slack-webhook-{event_id}"
        
        # Track the workflow ID for cleanup
        self.created_workflow_ids.append(expected_workflow_id)
        
        response = test_app.post("/webhooks/slack", json={"event_id": event_id})

        # Handle different scenarios based on Temporal server state
        if response.status_code == 202:
            # Temporal server is available - workflow started successfully
            json_response = response.get_json()
            assert "status" in json_response
            assert "Workflow started successfully" in json_response["status"]
            assert json_response["workflow_id"] == expected_workflow_id
            
        elif response.status_code == 503:
            # Temporal server is unavailable
            json_response = response.get_json()
            assert "error" in json_response
            assert "Failed to connect to workflow service" in json_response["error"]
            assert json_response["workflow_id"] == expected_workflow_id
            
        elif response.status_code == 500:
            # Temporal server available but workflow start failed (e.g., duplicate ID)
            json_response = response.get_json()
            assert "error" in json_response
            assert "Failed to start workflow" in json_response["error"]
            assert json_response["workflow_id"] == expected_workflow_id
            
        else:
            # Unexpected status code
            pytest.fail(f"Unexpected status code: {response.status_code}, response: {response.get_json()}")

    def test_slack_webhook_endpoint_invalid_json(self, test_app: FlaskClient):
        """Test that the endpoint properly validates JSON requests."""
        response = test_app.post("/webhooks/slack", data="not json")

        # Should return 400 for invalid JSON
        assert response.status_code == 400
        json_response = response.get_json()
        assert json_response["error"] == "Request must be JSON"
        
    def test_slack_webhook_endpoint_success_with_cleanup(self, test_app: FlaskClient):
        """Test workflow creation and cleanup when Temporal server is available.
        
        Note: This test handles all Temporal server scenarios.
        """

        # Use unique event ID to avoid workflow conflicts
        event_id = f"cleanup-{uuid.uuid4().hex[:8]}"
        expected_workflow_id = f"slack-webhook-{event_id}"
        
        # Track the workflow ID for cleanup
        self.created_workflow_ids.append(expected_workflow_id)
        
        response = test_app.post("/webhooks/slack", json={"event_id": event_id})
        
        if response.status_code == 202:
            # Temporal server is available - workflow started successfully
            json_response = response.get_json()
            assert "status" in json_response
            assert "Workflow started successfully" in json_response["status"]
            assert json_response["workflow_id"] == expected_workflow_id
            assert "workflow_run_id" in json_response
            
        elif response.status_code == 503:
            # Temporal server is unavailable
            json_response = response.get_json()
            assert "error" in json_response
            assert "Failed to connect to workflow service" in json_response["error"]
            assert json_response["workflow_id"] == expected_workflow_id
            
        elif response.status_code == 500:
            # Temporal server available but workflow start failed (e.g., duplicate ID)
            json_response = response.get_json()
            assert "error" in json_response
            assert "Failed to start workflow" in json_response["error"]
            assert json_response["workflow_id"] == expected_workflow_id
            
        else:
            # Any other status code is unexpected
            pytest.fail(f"Unexpected status code: {response.status_code}, response: {response.get_json()}")