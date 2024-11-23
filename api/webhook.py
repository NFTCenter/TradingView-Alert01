import os
import requests
from flask import Flask, request

# Initialize Flask app
app = Flask(__name__)

# Load environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Define the webhook route
@app.route('/api/webhook', methods=['POST'])
def webhook():
    try:
        # Parse incoming JSON payload
        data = request.get_json()
        message = data.get("text", "Alert Triggered")  # Default message if "text" is not provided

        # Send the message to Telegram
        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": message}
        response = requests.post(telegram_url, json=payload)

        # Return success or error response
        if response.status_code == 200:
            return "Notification sent successfully!", 200
        else:
            return f"Failed to send message to Telegram. Response: {response.text}", response.status_code
    except Exception as e:
        # Handle errors and return response
        return f"An error occurred: {str(e)}", 500

# This block is not necessary for serverless functions but useful for local testing
if __name__ == '__main__':
    app.run(debug=True)
