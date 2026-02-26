from flask import Blueprint, request
import requests
from config import Config
from routes.api import get_ai_answer, save_message_to_db

bp = Blueprint('telegram', __name__)

@bp.route('/api/telegram', methods=['POST'])
def telegram_webhook():
    update = request.get_json()
    if "message" in update and "text" in update["message"]:
        chat_id = update["message"]["chat"]["id"]
        user_text = update["message"]["text"]
        user_id = update["message"]["from"]["id"]
        user_first_name = update["message"]["from"].get("first_name", "User")
        
        print(f"\n📱 Telegram message received from {user_first_name} (ID: {user_id}): {user_text}")
        
        # ✅ Call the helper function to get AI response
        ai_response = get_ai_answer(user_text) 
        
        print(f"🤖 Telegram response: {ai_response[:100]}...")
        
        # Save message to database from Telegram source
        save_message_to_db(
            user_message=user_text,
            ai_response=ai_response,
            source="telegram",
            user_ip="",
            telegram_user_id=user_id
        )
        
        send_url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(send_url, json={"chat_id": chat_id, "text": ai_response})
        
        print(f"✅ Message sent to Telegram")
        
    return "ok", 200
