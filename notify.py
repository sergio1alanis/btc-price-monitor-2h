import os
import requests


def send_notifications(message: str) -> None:
    # Composio is used as the notification bridge. The workflow supplies COMPOSIO_API_KEY.
    # Keep destination details in repository secrets, never in source code.
    api_key = os.environ.get("COMPOSIO_API_KEY")
    if not api_key:
        raise RuntimeError("Missing COMPOSIO_API_KEY secret")

    # Placeholder contract: the GitHub workflow calls the Composio API endpoint with the
    # configured connected Gmail and Telegram actions. This module intentionally fails closed
    # until the endpoint/action identifiers are configured as repository secrets.
    composio_url = os.environ.get("COMPOSIO_API_URL", "")
    gmail_action = os.environ.get("COMPOSIO_GMAIL_ACTION", "")
    telegram_action = os.environ.get("COMPOSIO_TELEGRAM_ACTION", "")
    if not all([composio_url, gmail_action, telegram_action]):
        raise RuntimeError("Notification configuration is incomplete: COMPOSIO_API_URL, COMPOSIO_GMAIL_ACTION and COMPOSIO_TELEGRAM_ACTION are required")

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    for action in (gmail_action, telegram_action):
        r = requests.post(composio_url, headers=headers, json={"action": action, "message": message}, timeout=30)
        r.raise_for_status()
