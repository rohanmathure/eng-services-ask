#!/usr/bin/env python3

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker

# Import your workflow and activities
from workflows.request_start import RequestStart
from activities.slack import SlackActivity
from clients.temporal import TemporalClient

# Load environment variables
load_dotenv(".env.shared")
load_dotenv(".env.secret", override=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Start the Temporal worker."""
    try:
        # Get Temporal client
        logger.info("Connecting to Temporal server...")
        client = await TemporalClient.get_client()
        logger.info("Successfully connected to Temporal client")

        # Create activity instances
        slack_activity = SlackActivity()

        # Create and start worker
        logger.info("Starting Temporal worker...")
        worker = Worker(
            client,
            task_queue="slack-webhook-task-queue",
            workflows=[RequestStart],
            activities=[
                slack_activity.send_message,
                slack_activity.add_reaction,
                slack_activity.lookup_user_by_email,
            ],
            activity_executor=ThreadPoolExecutor(max_workers=5),
        )

        logger.info("Worker started! Waiting for workflows and activities...")
        await worker.run()
        
    except KeyboardInterrupt:
        logger.info("Worker shutdown requested")
    except Exception as e:
        logger.error(f"Worker error: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
