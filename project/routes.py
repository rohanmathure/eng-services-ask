from flask import Blueprint, jsonify, request

import logging

from clients.temporal import TemporalClient
from workflows.RequestStart import RequestStart

logger = logging.getLogger(__name__)


main_bp = Blueprint('main', __name__)
webhooks_bp = Blueprint('webhooks', __name__)

@main_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200


@webhooks_bp.route("/slack", methods=["POST"])
async def slack_webhook():
    """Handle incoming Slack webhooks and start Temporal workflow."""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    payload = request.get_json()
    logger.info(f"Received Slack webhook: {payload}")


    #TODO: Make it confirm to slack payload and also trigger it from a slack webhook

    # Start a workflow execution
    workflow_id = f"slack-webhook-{payload.get('event_id', 'unknown')}"
    client = await TemporalClient.get_client()

    client.start_workflow(
        RequestStart.run,
        payload,
        id=workflow_id,
        task_queue="slack-webhook-task-queue"
    )

    logger.info(f"Started workflow with ID: {workflow_id}")
    return jsonify({"status": "Workflow started", "workflow_id": workflow_id}), 202
