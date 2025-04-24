#!/usr/bin/env python3

from datetime import datetime
import sys

LOG_FILE = "app.log"

def log(level, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] [{level.upper()}] {message}"

    output = sys.stderr if level.lower() == "error" else sys.stdout
    print(formatted_message, file=output)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formatted_message + "\n")