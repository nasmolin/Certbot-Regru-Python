#!/usr/bin/env python3

import subprocess
import os
import sys
import threading
import time
from dotenv import load_dotenv
from notifier import send_telegram_message
from log_utils import log
import pathlib

try:
    sys.stdout.reconfigure(line_buffering=True)
except AttributeError:
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, line_buffering=True)

load_dotenv()

EMAIL = os.getenv("CERT_EMAIL")
DOMAIN = os.getenv("WILDCARD_DOMAIN")
LE_LOG_PATH = "/var/log/letsencrypt/letsencrypt.log"
APP_LOG_PATH = "app.log"

if not EMAIL or not DOMAIN:
    log("error", "CERT_EMAIL или WILDCARD_DOMAIN не заданы в .env")
    sys.exit(1)

CERTBOT_CMD = [
    "certbot", "certonly",
    "--manual",
    "--preferred-challenges", "dns",
    "--manual-auth-hook", "./manual_auth_hook.py",
    "--manual-cleanup-hook", "./manual_cleanup_hook.py",
    "--post-hook", "./post_hook.sh",
    "--agree-tos",
    "--no-eff-email",
    "--non-interactive",
    "--email", EMAIL,
    "-d", DOMAIN
]

def check_certbot_log_for_hook_errors():
    log_path = pathlib.Path(LE_LOG_PATH)

    if not log_path.exists():
        log("error", f"Let's Encrypt log file not found: {LE_LOG_PATH}")
        send_telegram_message("❌ *Let's Encrypt:* Ошибка при обновлении сертификата!")
        sys.exit(1)

    with log_path.open("r", encoding="utf-8") as log_file:
        content = log_file.read()
        if "[ERROR]" in content:
            log("error", "Let's Encrypt log contains `[ERROR]`. Something went wrong.")
            send_telegram_message("❌ *Let's Encrypt:* Ошибка при обновлении сертификата!")
            sys.exit(1)

def run_certbot():
    stop_event = threading.Event()

    def tail_and_print(path, stop_evt):
        while not stop_evt.is_set():
            if os.path.exists(path):
                break
            time.sleep(0.5)

        try:
            with open(path, "r", encoding="utf-8") as f:
                f.seek(0, os.SEEK_END)
                while not stop_evt.is_set():
                    line = f.readline()
                    if not line:
                        time.sleep(0.5)
                        continue
                    print(line, end='', flush=True)
        except Exception as e:
            print(f"[tailer error] {e}", file=sys.stderr, flush=True)

    tailer = threading.Thread(
        target=tail_and_print,
        args=(APP_LOG_PATH, stop_event),
        daemon=True
    )
    tailer.start()

    process = subprocess.Popen(CERTBOT_CMD)
    process.wait()

    stop_event.set()
    tailer.join(timeout=1)

    check_certbot_log_for_hook_errors()

    if process.returncode == 0:
        log("success", "Certificate obtained/renewed.")
        send_telegram_message("✅ *Let's Encrypt:* Сертификат успешно обновлён.")
        sys.exit(0)
    else:
        log("error", "Failed to get certificate.")
        send_telegram_message("❌ *Let's Encrypt:* Ошибка при обновлении сертификата!")
        sys.exit(1)

if __name__ == "__main__":
    run_certbot()