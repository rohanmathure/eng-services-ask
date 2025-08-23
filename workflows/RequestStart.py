import logging
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

from workflows.models.request import Request


logger = logging.getLogger(__name__)

@workflow.defn
class RequestStart:
    @workflow.run
    async def run(self, payload: any):
        # retry_policy = RetryPolicy(
        #     maximum_attempts=3,
        #     maximum_interval=timedelta(seconds=2),
        #     non_retryable_error_types=[],
        # )
        #TODO implement the workflow
         
        pass

    @workflow.query
    def get_request(self, request_id: str) -> Request:
        pass