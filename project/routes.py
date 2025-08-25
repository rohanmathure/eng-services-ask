from flask import Blueprint, jsonify, request

import logging

from clients.temporal import TemporalClient
from workflows.request_start import RequestStart

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

    # Generate workflow ID
    workflow_id = f"slack-webhook-{payload.get('event_id', 'unknown')}"
    
    try:
        # Connect to Temporal client
        logger.info("Connecting to Temporal client...")
        client = await TemporalClient.get_client()
        logger.info("Successfully connected to Temporal client")
        
    except Exception as e:
        logger.error(f"Failed to connect to Temporal server: {str(e)}")
        return jsonify({
            "error": "Failed to connect to workflow service",
            "details": str(e),
            "workflow_id": workflow_id
        }), 503

    try:
        # Start workflow execution
        logger.info(f"Starting workflow with ID: {workflow_id}")
        workflow_handle = await client.start_workflow(
            RequestStart.run,
            payload,
            id=workflow_id,
            task_queue="slack-webhook-task-queue"
        )
        
        # Verify workflow started successfully
        if workflow_handle:
            logger.info(f"Successfully started workflow with ID: {workflow_id}")
            return jsonify({
                "status": "Workflow started successfully", 
                "workflow_id": workflow_id,
                "workflow_run_id": workflow_handle.id
            }), 202
        else:
            logger.error(f"Workflow handle is None for workflow ID: {workflow_id}")
            return jsonify({
                "error": "Workflow started but handle is invalid",
                "workflow_id": workflow_id
            }), 500
            
    except Exception as e:
        logger.error(f"Failed to start workflow {workflow_id}: {str(e)}")
        return jsonify({
            "error": "Failed to start workflow",
            "details": str(e),
            "workflow_id": workflow_id
        }), 500
