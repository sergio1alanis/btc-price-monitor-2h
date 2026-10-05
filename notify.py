import os
import requests

COMPOSIO_URL = "https://backend.composio.dev/api/v3.1/tools/execute"


def execute_tool(api_key: str, slug: str, connected_account_id: str, arguments: dict) -> None:
    r = requests.post(
        f"{COMPOSIO_URL}/{slug}",
        headers={"x-api-key": api_key, "Content-Type": "application/json"},
        json={"connected_account_id": connected_account_id, "version": "latest", "arguments": arguments},
        timeout=45,
    )
    if not r.ok:
        try:
            detail = r.json()
        except ValueError:
            detail = r.text
        raise RuntimeError(f"Composio {slug} HTTP {r.status_code}: {detail}")
    payload = r.json()
    if payload.get("successful") is False:
        raise RuntimeError(f"Composio {slug} failed: {payload.get('error')}")


def send_notifications(message: str) -> None:
    api_key = os.environ.get("COMPOSIO_API_KEY")
    gmail_account = os.environ.get("GMAIL_CONNECTED_ACCOUNT_ID")
    telegram_account = os.environ.get("TELEGRAM_CONNECTED_ACCOUNT_ID")
    telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    gmail_recipient = os.environ.get("GMAIL_RECIPIENT")
    if not all([api_key, gmail_account, telegram_account, telegram_chat_id, gmail_recipient]):
        raise RuntimeError("Missing notification secrets")

    subject = "Bitcoin — reporte automático cada 2 horas"
    errors = []
    try:
        execute_tool(api_key, "GMAIL_SEND_EMAIL", gmail_account, {
            "recipient_email": gmail_recipient,
            "subject": subject,
            "body": message,
            "is_html": False,
        })
    except Exception as exc:
        errors.append(f"Gmail: {exc}")

    try:
        execute_tool(api_key, "TELEGRAM_SEND_MESSAGE", telegram_account, {
            "chat_id": telegram_chat_id,
            "text": message,
        })
    except Exception as exc:
        errors.append(f"Telegram: {exc}")

    if errors:
        raise RuntimeError("Notification failures: " + " | ".join(errors))
