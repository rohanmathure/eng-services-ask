import logging
import os
from dotenv import load_dotenv

from temporalio.client import Client
from temporalio.worker import Worker

# Load environment variables from dotenv files
load_dotenv(".env.shared")
load_dotenv(".env.secret", override=True)

logger = logging.getLogger(__name__)

# Temporal client connection
async def start_temporal_client():
    """Connect to the Temporal server."""
    temporal_address = os.getenv("TEMPORAL_ADDRESS", "localhost:7233")
    temporal_namespace = os.getenv("TEMPORAL_NAMESPACE", "default")
    api_key = os.getenv("TEMPORAL_API_KEY")
    
    logger.info(f"Connecting to Temporal at {temporal_address}, namespace {temporal_namespace}")
    
    # Configure TLS for Temporal Cloud
    tls_config = None
    if temporal_address and 'temporal.io' in temporal_address:
        from temporalio.client import TLSConfig
        tls_config = TLSConfig()  # Use default TLS for Temporal Cloud
    
    return await Client.connect(
        temporal_address, 
        namespace=temporal_namespace,
        api_key=api_key if api_key else None,
        tls=tls_config
    )


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