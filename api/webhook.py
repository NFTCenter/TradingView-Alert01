import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Load environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

@app.route('/api/webhook', methods=['POST'])
def webhook():
    try:
        # Parse incoming JSON
        data = request.get_json()
        message = data.get("text", "Alert Triggered")

        # Send message to Telegram
        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": message}
        response = requests.post(telegram_url, json=payload)

        if response.status_code == 200:
            return "Notification sent", 200
        else:
            return f"Failed to send message: {response.text}", 500
    except Exception as e:
        return f"Error: {e}", 500
