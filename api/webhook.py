import os
import requests
from flask import Flask, request

# Initialize Flask app
app = Flask(__name__)

# CoinMarketCap API Configuration
CMC_API_KEY = os.getenv("CMC_API")  # API key from Vercel environment variables
CMC_URL = "https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest"
USDT_D_THRESHOLD = 3.8  # Set your target dominance threshold

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Telegram bot token
CHAT_ID = os.getenv("CHAT_ID")  # Telegram chat ID


def send_telegram_alert(message):
    """Send a notification to Telegram."""
    try:
        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": message}
        response = requests.post(telegram_url, json=payload)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error sending Telegram alert: {e}")
        return False


def get_usdt_dominance():
    """Fetch USDT dominance using CoinMarketCap API."""
    headers = {"X-CMC_PRO_API_KEY": CMC_API_KEY}

    try:
        response = requests.get(CMC_URL, headers=headers)
        response.raise_for_status()
        data = response.json()
        print("CoinMarketCap API Response:", data)  # Debugging

        # Extract stablecoin and total market cap
        stablecoin_market_cap = data["data"]["stablecoin_market_cap"]
        total_market_cap = data["data"]["quote"]["USD"]["total_market_cap"]

        # Calculate USDT dominance as 74% of stablecoin market cap
        usdt_market_cap = 0.74 * stablecoin_market_cap
        usdt_dominance = (usdt_market_cap / total_market_cap) * 100
        return usdt_dominance

    except Exception as e:
        print(f"Error fetching data from CoinMarketCap: {e}")
        return None


@app.route("/api/webhook", methods=["POST"])
def monitor_usdt():
    """Monitor USDT dominance."""
    dominance = get_usdt_dominance()
    if dominance is None:
        return {"error": "Failed to fetch USDT dominance"}, 500

    if dominance <= USDT_D_THRESHOLD:
        message = f"🚨 Alert! USDT Dominance has dropped to {dominance:.2f}%!"
        if send_telegram_alert(message):
            return {"message": "Alert sent successfully!", "usdt_dominance": dominance}, 200
        else:
            return {"error": "Failed to send Telegram alert"}, 500
    else:
        return {"message": f"USDT Dominance is currently {dominance:.2f}%, above the threshold."}, 200


@app.route("/test-env", methods=["GET"])
def test_env():
    """Test environment variables."""
    return {
        "CMC_API": CMC_API_KEY is not None,
        "CHAT_ID": CHAT_ID is not None,
        "TELEGRAM_BOT_TOKEN": TELEGRAM_BOT_TOKEN is not None,
    }


if __name__ == "__main__":
    app.run(debug=True)  # For local testing only
