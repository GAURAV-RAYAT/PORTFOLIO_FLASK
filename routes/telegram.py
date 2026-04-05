from flask import Blueprint, request
import requests
from config import Config
from routes.api import get_ai_answer, save_message_to_db

bp = Blueprint('telegram', __name__)

@bp.route('/api/telegram', methods=['POST'])
def telegram_webhook():
    # Verify the request is from Telegram using the webhook secret token
    if Config.TELEGRAM_WEBHOOK_SECRET:
        incoming_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if incoming_secret != Config.TELEGRAM_WEBHOOK_SECRET:
            return "Unauthorized", 401

    update = request.get_json()
    if not update:
        return "ok", 200
    if "message" in update and "text" in update["message"]:
        chat_id = update["message"]["chat"]["id"]
        user_text = update["message"]["text"]
        user_id = update["message"]["from"]["id"]
        ai_response = get_ai_answer(user_text)
        save_message_to_db(
            user_message=user_text,
            ai_response=ai_response,
            source="telegram",
            user_ip="",
            telegram_user_id=user_id
        )
        send_url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(send_url, json={"chat_id": chat_id, "text": ai_response})
    return "ok", 200
