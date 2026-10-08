"""Register the API Gateway URL and webhook secret with Telegram.

Usage: python scripts/set_webhook.py <WebhookUrl from the stack outputs>
Needs AWS credentials for the team account and AWS_DEFAULT_REGION set to the stack's region.
"""
import os
import sys

import boto3
import requests


def get_secret(name: str) -> str:
    ssm = boto3.client("ssm")
    return ssm.get_parameter(Name=name, WithDecryption=True)["Parameter"]["Value"]


def main(url: str) -> None:
    if not url.startswith("https://"):
        sys.exit("Telegram only accepts https webhook URLs")
    token = get_secret(os.environ.get("TELEGRAM_TOKEN_PARAM", "/hackathon/telegram_token"))
    secret = get_secret(os.environ.get("WEBHOOK_SECRET_PARAM", "/hackathon/webhook_secret"))
    resp = requests.post(
        f"https://api.telegram.org/bot{token}/setWebhook",
        json={
            "url": url,
            "secret_token": secret,
            "allowed_updates": ["message", "callback_query"],
        },
        timeout=10,
    )
    # Print Telegram's verdict only; the request URL contains the token.
    print(resp.status_code, resp.json().get("description"))
    if not resp.ok:
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
