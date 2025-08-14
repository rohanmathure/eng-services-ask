import os
import logging
from flask import Flask, request, jsonify
from temporalio.client import Client
from temporalio.worker import Worker
import asyncio

# Import workflow and activity modules
from workflows.trigger_workflow_new_message import TriggerWorkflowNewMessage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Temporal client connection
async def start_temporal_client():
    """Connect to the Temporal server."""
    temporal_address = os.getenv("TEMPORAL_ADDRESS", "localhost:7233")
    temporal_namespace = os.getenv("TEMPORAL_NAMESPACE", "default")
    
    logger.info(f"Connecting to Temporal at {temporal_address}, namespace {temporal_namespace}")
    return await Client.connect(temporal_address, namespace=temporal_namespace)


# Start Temporal worker
async def start_worker(client):
    """Start a Temporal worker to process workflows and activities."""
    # Initialize activity implementations
    
    logger.info("Starting Temporal worker")
    worker = Worker(
        client,
        task_queue="slack-webhook-task-queue",
        workflows=[TriggerWorkflowNewMessage],
        activities=[

        ]
    )
    await worker.run()


# Webhook endpoint for Slack
@app.route("/webhook/slack", methods=["POST"])
async def slack_webhook():
    """Handle incoming Slack webhooks and start Temporal workflow."""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    payload = request.get_json()
    logger.info(f"Received Slack webhook: {payload}")
    
    # Connect to Temporal
    client = await start_temporal_client()
    
    # Start a workflow execution
    workflow_id = f"slack-webhook-{payload.get('event_id', 'unknown')}"
    await client.start_workflow(
        TriggerWorkflowNewMessage.run,
        payload,
        id=workflow_id,
        task_queue="slack-webhook-task-queue"
    )
    
    logger.info(f"Started workflow with ID: {workflow_id}")
    return jsonify({"status": "Workflow started", "workflow_id": workflow_id}), 202


# Health check endpoint
@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    # Start the Temporal worker in a background task
    client = None
    
    async def startup():
        global client
        client = await start_temporal_client()
        asyncio.create_task(start_worker(client))
    
    # Run startup code
    loop = asyncio.get_event_loop()
    loop.run_until_complete(startup())
    
    # Start Flask app
    port = int(os.getenv("PORT", 8888))
    app.run(host="0.0.0.0", port=port)