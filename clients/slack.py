import os
import logging
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Load environment variables from dotenv files
load_dotenv(".env.shared")
load_dotenv(".env.secret", override=True)

logger = logging.getLogger(__name__)


class SlackClient:
    """Slack API client that uses token from environment variables."""
    
    _client = None
    _instance = None
    
    def __init__(self, token=None):
        """Initialize Slack client with token from environment or parameter."""
        if token is None:
            token = os.getenv("SLACK_BOT_TOKEN")
            
        if not token:
            raise ValueError("Slack bot token not found. Set SLACK_BOT_TOKEN in environment or .env files.")
            
        self.client = WebClient(token=token)
        logger.info("Slack client initialized successfully")
    
    @classmethod
    def get_client(cls):
        """Get a singleton instance of the Slack client."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def send_message(self, channel, text, **kwargs):
        """Send a message to a Slack channel."""
        try:
            logger.info(f"Sending message to channel {channel}")
            response = self.client.chat_postMessage(
                channel=channel,
                text=text,
                **kwargs
            )
            logger.info(f"Message sent successfully. Timestamp: {response['ts']}")
            return response
        except SlackApiError as e:
            logger.error(f"Error sending message to {channel}: {e.response['error']}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error sending message: {str(e)}")
            raise

    def add_reaction(self, channel, message_ts, emoji):
        """Add an emoji reaction to a message."""
        try:
            logger.info(f"Adding reaction {emoji} to message {message_ts} in {channel}")
            response = self.client.reactions_add(
                channel=channel,
                timestamp=message_ts,
                name=emoji
            )
            logger.info(f"Reaction added successfully")
            return response
        except SlackApiError as e:
            logger.error(f"Error adding reaction: {e.response['error']}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error adding reaction: {str(e)}")
            raise

    def get_user_from_email(self, email):
        """Get user information by email address."""
        try:
            logger.info(f"Looking up user by email: {email}")
            response = self.client.users_lookupByEmail(email=email)
            user = response['user']
            logger.info(f"Found user: {user.get('name', 'Unknown')} ({user['id']})")
            return user
        except SlackApiError as e:
            logger.error(f"Error looking up user by email {email}: {e.response['error']}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error looking up user: {str(e)}")
            raise
            
    def chat_postMessage(self, **kwargs):
        """Direct access to chat.postMessage API (for backwards compatibility)."""
        return self.send_message(**kwargs)