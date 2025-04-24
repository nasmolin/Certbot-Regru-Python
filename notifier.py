#!/usr/bin/env python3

import os
import requests
from datetime import datetime
import sys
from log_utils import log

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        log("warn", "Telegram not configured, skipping message.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, data=data)
        if response.status_code != 200:
            log("error", f"Telegram response: {response.text}")
    except Exception as e:
        log("error", f"Telegram exception: {e}")
