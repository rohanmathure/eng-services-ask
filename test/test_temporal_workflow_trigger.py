from flask.testing import FlaskClient

class TestTemporalWorkflowTrigger:
    def test_temporal_workflow_trigger(self, test_app: FlaskClient):
        response = test_app.post("/webhooks/slack", json={"event_id": "foobar"})
        assert response.status_code == 202