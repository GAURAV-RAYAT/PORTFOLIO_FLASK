from flask import Blueprint, request, jsonify
import requests
from config import Config
from utils.resume_parser import get_beautified_resume
from routes.api import save_message_to_db

bp = Blueprint('chat', __name__)

# --- RESUME DATA CONTEXT ---
resume_context = get_beautified_resume()
SYSTEM_PROMPT = f"""
    You are the AI Assistant for Gaurav Rayat. 
    Use the following resume data to answer questions:
    
    {resume_context}
    
    KEEP THE ANSWERS CONCISE AND RELEVANT TO THE RESUME DATA GIVEN TO YOU.
    DO NOT MAKE UP ANSWERS OR ADD ANY INFORMATION NOT PRESENT IN THE RESUME DATA.
    IF YOU DON'T KNOW THE ANSWER, SAY YOU DON'T KNOW INSTEAD OF MAKING UP AN ANSWER.
    ALWAYS REFER TO THE RESUME DATA FOR ANSWERS AND DO NOT ADD ANY PERSONAL OPINIONS OR ASSUMPTIONS.
    If you got /start as input, reply with a welcome message and brief instructions on how to ask questions about the resume.
    """

@bp.route("/chat", methods=["POST"])
def chat():
    print("\n🤖 Chat endpoint accessed!")
    data = request.get_json()
    user_message = data.get("message", "").strip()
    
    print(f"📨 User message received: {user_message}")

    if not user_message:
        print("❌ Empty message!")
        return jsonify({"response": "Please enter a valid message."})

    try:
        headers = {
            "Authorization": f"Bearer {Config.OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "openai/gpt-4o-mini",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ]
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload
        )
        response_data = response.json()
        
        if "choices" in response_data:
            reply = response_data["choices"][0]["message"]["content"].strip()
            print(f"🤖 AI Response generated: {reply[:100]}...")
        else:
            print("API Error:", response_data)
            reply = "I'm having trouble connecting right now. Please try again."

    except Exception as e:
        print("Server Error:", e)
        return jsonify({"response": "An internal error occurred."})

    # Save message to MongoDB from web source
    save_message_to_db(
        user_message=user_message,
        ai_response=reply,
        source="web",
        user_ip=request.remote_addr
    )

    return jsonify({"response": reply})
