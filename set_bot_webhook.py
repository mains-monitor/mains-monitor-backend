import os
import urllib.parse
import requests
from dotenv import load_dotenv

load_dotenv()

# Get the Telegram token and URL from environment variables
telegram_token = os.environ.get("TELEGRAM_TOKEN")
url = os.environ.get("BOT_WEBHOOK_URL")

# URL encode the URL
url_encoded = urllib.parse.quote(url)

# Construct the API URL
api_url = f"https://api.telegram.org/bot{telegram_token}/setWebhook?url={url_encoded}"

# Send the HTTP GET request
response = requests.get(api_url)

# Check the response status code
if response.status_code == 200:
    print("Webhook set successfully!")
else:
    print("Failed to set webhook.")
