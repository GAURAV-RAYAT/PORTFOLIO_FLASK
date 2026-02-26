from flask import Blueprint, request, jsonify
import requests
from config import Config
from utils.resume_parser import get_beautified_resume

bp = Blueprint('chat', __name__)

# --- RESUME DATA CONTEXT ---
resume_context = get_beautified_resume()
SYSTEM_PROMPT = f"""
    You are the AI Assistant for Gaurav Rayat. 
    Use the following resume data to answer questions:
    
    {resume_context}
    
    Behavior: Keep answers concise and only use the provided facts.
    """

@bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
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
        else:
            print("API Error:", response_data)
            reply = "I'm having trouble connecting right now. Please try again."

    except Exception as e:
        print("Server Error:", e)
        return jsonify({"response": "An internal error occurred."})

    return jsonify({"response": reply})
