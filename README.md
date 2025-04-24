# Let's Encrypt Certificate Automation with Reg.ru and GitLab CI

Automation of obtaining Let's Encrypt wildcard certificates via DNS validation using the [Reg.ru](https://www.reg.ru/) API and GitLab CI/CD pipeline. Supports Telegram notifications and artifact collection.

---

## Features
⚠️ For proper operation of certbot DNS challenge, make sure your DNS records update quickly enough (use a low TTL).

- Generate or renew Let's Encrypt wildcard certificates
- DNS validation via Reg.ru API
- Telegram notifications
- Collection of logs and certificates as GitLab artifacts
- Certbot log analysis for success verification

---

## Project Structure
```
.
├── .gitlab-ci.yml
├── .env.example
├── get_certificate.py        # Main script for obtaining the certificate
├── generate_artifacts.py     # Artifact collection script
├── manual_auth_hook.py       # DNS hook for Reg.ru (adds TXT record)
├── manual_cleanup_hook.py    # DNS hook to remove TXT record
├── post_hook.sh              # Post-hook script after certbot execution
├── log_utils.py              # Logging utility
└── app.log                   # Execution log (generated automatically)
```

---

## .env

⚠️ Make sure the IP address of your GitLab Runner is added to the allowed IPs in your Reg.ru API settings.
```dotenv
# Let's Encrypt
CERT_EMAIL=example@example.com       # Email for Let's Encrypt registration
WILDCARD_DOMAIN=*.example.com        # Domain for which the certificate is requested

# Reg.ru
REG_RU_USERNAME=user@example.com     # Login (email)
REG_RU_PASSWORD=api_token            # API token (! don't forget to whitelist the IP in Reg.ru API settings)
REG_RU_DOMAIN_ZONE=example.com       # Domain zone (without subdomains)

# Telegram
TELEGRAM_TOKEN=123456:ABC...         # Telegram bot token
TELEGRAM_CHAT_ID=-123456789          # Chat ID (you can get it via @get_id_bot)

# DNS propagation
MAX_ATTEMPTS=36                      # Number of DNS check attempts (every 5 minutes)
DELAY=300                            # Delay between checks in seconds
```

---

## Artifacts

After the pipeline execution, the following artifacts are saved:
 - Let's Encrypt certificates (`/etc/letsencrypt`)
 - Certbot log (`/var/log/letsencrypt/letsencrypt.log`)
 - Execution log (`app.log`)
