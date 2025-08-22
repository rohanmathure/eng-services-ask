import logging
import os
from project.app import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


app = create_app()

if __name__ == "__main__":
    # Start Flask app
    port = int(os.getenv("PORT", 8888))
    app.run(host="0.0.0.0", port=port)