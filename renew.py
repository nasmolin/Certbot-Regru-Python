#!/usr/bin/env python3

import os
import subprocess
from dotenv import load_dotenv
from datetime import datetime
import sys
from log_utils import log

load_dotenv()

cmd = [
    "certbot", "renew",
    "--manual-auth-hook", "./manual_auth_hook.py",
    "--manual-cleanup-hook", "./manual_cleanup_hook.py",
    "--post-hook", "./post_hook.sh",
    "--manual-public-ip-logging-ok",
    "--deploy-hook", "./post_hook.sh"
]

res = subprocess.run(cmd)
if res.returncode == 0:
    log("success", "Renewed certificates (if needed).")
else:
    log("error", "Failed to renew certificates.")
