# Let's Encrypt Certificate Automation with Reg.ru and GitLab CI

Автоматизация получения wildcard сертификатов Let's Encrypt через DNS валидацию с использованием API [Reg.ru](https://www.reg.ru/) и CI/CD пайплайна GitLab. Поддерживается уведомление в Telegram и сбор артефактов.

---

## Возможности
⚠️ Для корректной работы certbot DNS challenge убедитесь, что ваши DNS-записи обновляются достаточно быстро (используйте небольшое TTL).

- Генерация или обновление wildcard-сертификатов Let's Encrypt
- DNS-валидация через Reg.ru API
- Уведомления в Telegram
- Сбор логов и сертификатов как артефактов GitLab
- Проверка успешности выполнения через анализ логов certbot

---

## Структура проекта
```
.
├── .gitlab-ci.yml
├── .env.example
├── get_certificate.py        # Основной скрипт получения сертификата
├── generate_artifacts.py     # Сбор артефактов
├── manual_auth_hook.py       # DNS-хук для Reg.ru (создание TXT записи)
├── manual_cleanup_hook.py    # DNS-хук для удаления TXT записи
├── post_hook.sh              # Post-хук после certbot
├── log_utils.py              # Утилита логирования
└── app.log                   # Лог выполнения (создаётся автоматически)
```

---

## .env

⚠️ Убедитесь, что IP-адрес GitLab Runner'а добавлен в список разрешённых IP Reg.ru API.
```dotenv
# Let's Encrypt
CERT_EMAIL=example@example.com       # Email для регистрации в Let's Encrypt
WILDCARD_DOMAIN=*.example.com        # Домен, для которого запрашивается сертификат

# Reg.ru
REG_RU_USERNAME=user@example.com     # Логин (email)
REG_RU_PASSWORD=api_token            # API токен ( ! добавьте IP в настройках Reg.ru API)
REG_RU_DOMAIN_ZONE=example.com       # Зона домена (без поддоменов)

# Telegram
TELEGRAM_TOKEN=123456:ABC...         # Токен Telegram бота
TELEGRAM_CHAT_ID=-123456789          # ID чата (можно узнать через @get_id_bot)

# DNS propagation
MAX_ATTEMPTS=36                      # Кол-во попыток проверки DNS (по 5 минут каждая)
DELAY=300                            # Задержка между проверками, в секундах
```

---

## Артефакты

После выполнения пайплайна, в артефактах сохраняются:
 - Сертификаты Let's Encrypt (/etc/letsencrypt)
 - Лог Certbot (/var/log/letsencrypt/letsencrypt.log)
 - Лог выполнения (app.log)