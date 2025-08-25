import logging
from temporalio import activity
from clients.slack import SlackClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)


class SlackActivity:
    """Temporal activities for Slack operations."""
    
    def __init__(self):
        self.slack_client = SlackClient.get_client()

    @activity.defn
    def send_message(self, channel: str, message: str, **kwargs):
        """Send a message to a Slack channel."""
        try:
            logger.info(f"Slack activity: sending message to {channel}")
            response = self.slack_client.send_message(channel=channel, text=message, **kwargs)
            return {
                "success": True,
                "timestamp": response.get("ts"),
                "channel": response.get("channel"),
                "message": message
            }
        except SlackApiError as e:
            logger.error(f"Slack API error in send_message: {e.response['error']}")
            return {
                "success": False,
                "error": e.response['error'],
                "message": message
            }
        except Exception as e:
            logger.error(f"Unexpected error in send_message: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": message
            }
            
    @activity.defn
    def add_reaction(self, channel: str, message_ts: str, emoji: str):
        """Add an emoji reaction to a message."""
        try:
            logger.info(f"Slack activity: adding reaction {emoji} to message {message_ts}")
            response = self.slack_client.add_reaction(channel=channel, message_ts=message_ts, emoji=emoji)
            return {
                "success": True,
                "channel": channel,
                "message_ts": message_ts,
                "emoji": emoji
            }
        except SlackApiError as e:
            logger.error(f"Slack API error in add_reaction: {e.response['error']}")
            return {
                "success": False,
                "error": e.response['error'],
                "emoji": emoji
            }
        except Exception as e:
            logger.error(f"Unexpected error in add_reaction: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "emoji": emoji
            }

    @activity.defn
    def lookup_user_by_email(self, email: str):
        """Look up a Slack user by email address."""
        try:
            logger.info(f"Slack activity: looking up user by email {email}")
            user = self.slack_client.get_user_from_email(email)
            return {
                "success": True,
                "user_id": user["id"],
                "username": user.get("name"),
                "real_name": user.get("real_name"),
                "email": email
            }
        except SlackApiError as e:
            logger.error(f"Slack API error in lookup_user_by_email: {e.response['error']}")
            return {
                "success": False,
                "error": e.response['error'],
                "email": email
            }
        except Exception as e:
            logger.error(f"Unexpected error in lookup_user_by_email: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "email": email
            }