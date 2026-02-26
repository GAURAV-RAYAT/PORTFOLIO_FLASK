from flask import Blueprint, request
import requests
from config import Config
from routes.api import get_ai_answer

bp = Blueprint('telegram', __name__)

@bp.route('/api/telegram', methods=['POST'])
def telegram_webhook():
    update = request.get_json()
    if "message" in update and "text" in update["message"]:
        chat_id = update["message"]["chat"]["id"]
        user_text = update["message"]["text"]
        
        # ✅ Call the helper function to get AI response
        ai_response = get_ai_answer(user_text) 
        
        send_url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(send_url, json={"chat_id": chat_id, "text": ai_response})
        
    return "ok", 200
