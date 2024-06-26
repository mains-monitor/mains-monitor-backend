#!/bin/bash

# https://api.telegram.org/bot{my_bot_token}/setWebhook?url={url_to_send_updates_to}

curl --data-urlencode "url=${BOT_WEBHOOK_URL}" "https://api.telegram.org/bot${TELEGRAM_TOKEN}/setWebhook"