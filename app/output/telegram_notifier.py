"""Raw Telegram Bot API access — send a message only, no config/env knowledge here."""

import requests

BASE_URL = "https://api.telegram.org/bot{token}/sendMessage"


class TelegramError(Exception):
    pass


def send_message(bot_token: str, chat_id: str, text: str) -> None:
    url = BASE_URL.format(token=bot_token)
    response = requests.post(url, data={"chat_id": chat_id, "text": text}, timeout=15)
    if response.status_code != 200:
        raise TelegramError(f"Telegram error ({response.status_code}): {response.text}")
