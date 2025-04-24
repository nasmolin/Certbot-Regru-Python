#!/usr/bin/env python3

import requests
import os
import sys
import json
from dotenv import load_dotenv
import time
import subprocess
from datetime import datetime
from log_utils import log

load_dotenv()

MAX_ATTEMPTS = int(os.getenv("MAX_ATTEMPTS"))
DELAY = int(os.getenv("DELAY"))

REG_RU_USERNAME = os.getenv("REG_RU_USERNAME")
REG_RU_PASSWORD = os.getenv("REG_RU_PASSWORD")

REG_RU_DOMAIN_ZONE = os.getenv("REG_RU_DOMAIN_ZONE")

if not MAX_ATTEMPTS or not DELAY:
    log("error", "MAX_ATTEMPTS или DELAY не заданы в .env")
    exit(1)

if not REG_RU_USERNAME or not REG_RU_PASSWORD:
    log("error", "REG_RU_USERNAME или REG_RU_PASSWORD не заданы в .env")
    exit(1)

def delete_dns_record(domain_zone, wildcard_domain, validation_token):
    subdomain = wildcard_domain.replace(f".{domain_zone}", "").replace("*", "_acme-challenge")

    input_data = {
        "username": REG_RU_USERNAME,
        "password": REG_RU_PASSWORD,
        "domains": [{ "dname": domain_zone }],
        "subdomain": subdomain,
        "content": validation_token,
        "output_content_type": "json",
        "record_type": "TXT"
    }

    regru_api_url = "https://api.reg.ru/api/regru2/zone/remove_record"
    post_data = {
        "input_format": "json",
        "input_data": json.dumps(input_data)
    }

    try:
        resp = requests.post(regru_api_url, data=post_data)
        resp.raise_for_status()
    except requests.RequestException as e:
        log("error", f"Failed to delete DNS record: {e}")
        sys.exit(1)

    try:
        data = resp.json()
    except json.JSONDecodeError:
        log("error", f"Invalid JSON in response: {resp.text}")
        sys.exit(1)

    if data.get("result") != "success":
        log("error", f"REG.RU API error: {data}")
        sys.exit(1)

    log("success", f"DNS-TXT record was deleted on Reg.ru for subdomain: {subdomain}")
    log("info", f"Waiting for the txt record to be removed from Reg.ru's DNS servers")
    log("info", f"Parameters: max_attempts={MAX_ATTEMPTS}, delay={DELAY}s")

    attempt_counter = 0
    while attempt_counter < MAX_ATTEMPTS:
        result = subprocess.run(
            ["dig", "-t", "txt", f"{subdomain}.{domain_zone}", "@ns1.reg.ru", "+short"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if not result.stdout.decode().strip():
            log("success", f"TXT-record successfully removed after ~{(attempt_counter * DELAY) / 60}m.")
            return

        log("info", f"({attempt_counter+1}/{MAX_ATTEMPTS}) The TXT-record is still present")
        attempt_counter += 1
        time.sleep(DELAY)

    log("error", "Max attempts reached")
    sys.exit(1)

if __name__ == "__main__":
    token = os.getenv("CERTBOT_VALIDATION")
    domain_zone = os.getenv("REG_RU_DOMAIN_ZONE")
    wildcard_domain = os.getenv("WILDCARD_DOMAIN")
    
    if not token or not domain_zone or not wildcard_domain:
        log("error", "CERTBOT_VALIDATION or REG_RU_DOMAIN_ZONE or WILDCARD_DOMAIN is undefined")
        sys.exit(1)

    delete_dns_record(domain_zone, wildcard_domain, token)
