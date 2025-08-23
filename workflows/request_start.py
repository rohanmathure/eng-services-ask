import logging
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

from models.request import Request
from activities.slack import SlackActivity


logger = logging.getLogger(__name__)

@workflow.defn
class RequestStart:
    @workflow.run
    async def run(self, payload: any):
        retry_policy = RetryPolicy(
            maximum_attempts=3,
            maximum_interval=timedelta(seconds=2),
            non_retryable_error_types=[],
        )


       # Acknowledge the request in Slack. For now we are only going to send a test message
       # to make sure that our temporal setup is working and we can create an activity
        slack_output = await workflow.execute_activity_method(
            SlackActivity.send_message,
            "#tmp-rohan-test",
            "Hello, world!",
            start_to_close_timeout=timedelta(seconds=5),
            retry_policy=retry_policy,
        )

    @workflow.query
    def get_request(self, request_id: str) -> Request:
        pass