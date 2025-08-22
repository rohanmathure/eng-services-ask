import logging
import os

from temporalio.client import Client
from temporalio.worker import Worker

logger = logging.getLogger(__name__)

# Temporal client connection
async def start_temporal_client():
    """Connect to the Temporal server."""
    temporal_address = os.getenv("TEMPORAL_ADDRESS", "localhost:7233")
    temporal_namespace = os.getenv("TEMPORAL_NAMESPACE", "default")
    
    logger.info(f"Connecting to Temporal at {temporal_address}, namespace {temporal_namespace}")
    return await Client.connect(temporal_address, namespace=temporal_namespace)


class TemporalClient:
    _client = None

    def __init__(self):
        if not self._client:
            raise RuntimeError("Temporal client not initialized. Call get_client() first.")
        
        return self._client

    @classmethod
    async def get_client(cls):
        if cls._client is None:
            cls._client = await start_temporal_client()
        return cls._client