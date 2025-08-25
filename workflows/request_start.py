import logging
from datetime import timedelta
import uuid
import datetime

from temporalio import workflow
from temporalio.common import RetryPolicy

from models.request import Request


logger = logging.getLogger(__name__)

@workflow.defn
class RequestStart:
    @workflow.run
    async def run(self, payload: dict):
        retry_policy = RetryPolicy(
            maximum_attempts=3,
            maximum_interval=timedelta(seconds=2),
            non_retryable_error_types=[],
        )


        # Acknowledge the request in Slack. For now we are only going to send a test message
        # to make sure that our temporal setup is working and we can create an activity
        slack_output = await workflow.execute_activity(
            "send_message",
            args=["#tmp-rohan-test", f"Hello from workflow! Event: {payload.get('event_id', 'unknown')}"],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry_policy,
        )
        
        return {
            "status": "completed",
            "event_id": payload.get('event_id', 'unknown'),
            "slack_message_result": slack_output
        }

    @workflow.query
    def get_request(self, request_id: str) -> Request:
        pass