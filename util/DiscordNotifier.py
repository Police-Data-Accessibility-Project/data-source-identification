import logging

import requests


class DiscordPoster:
    def __init__(self, webhook_url: str):
        if not webhook_url:
            logging.error("WEBHOOK_URL environment variable not set")
            raise ValueError("WEBHOOK_URL environment variable not set")
        self.webhook_url = webhook_url
    def post_to_discord(self, message):
        try:
            requests.post(self.webhook_url, json={"content": message})
        except Exception as e:
            logging.error(
                f"Error posting message to Discord: {e}."
                f"\n\nMessage: {message}"
            )
