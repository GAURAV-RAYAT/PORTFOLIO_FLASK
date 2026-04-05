from flask import Blueprint, request, jsonify
from langchain_openai import ChatOpenAI
from config import Config
from utils.resume_parser import get_trained_context
from utils.mail_helper import send_ai_message_notification_email
from database import get_collection
from datetime import datetime

bp = Blueprint('api', __name__)

def save_message_to_db(user_message, ai_response, source="web", user_ip="", telegram_user_id=None):
    """Save conversation to MongoDB from any source and send email notification"""
    try:
        chat_collection = get_collection("ai_messages")
        if chat_collection is not None:
            chat_document = {
                "user_message": user_message,
                "ai_response": ai_response,
                "timestamp": datetime.now(),
                "source": source,  # 'web', 'telegram', 'api'
                "user_ip": user_ip,
                "telegram_user_id": telegram_user_id
            }
            result = chat_collection.insert_one(chat_document)
            print(f"✅ Message saved from {source}! ID: {result.inserted_id}")
            
            # Send email notification for all AI messages
            send_ai_message_notification_email(
                user_message=user_message,
                ai_response=ai_response,
                source=source,
                telegram_user_id=telegram_user_id,
                user_ip=user_ip if source in ["web", "api"] else ""
                )
            
            return True
    except Exception as e:
        print(f"❌ Error saving message: {e}")
        import traceback
        traceback.print_exc()
    return False

def get_ai_answer(user_query):
    """Shared logic for API and Telegram."""
    try:
        # 1. Get the context from PDFs
        context_chunks = get_trained_context()

        # 2. Setup LLM
        llm = ChatOpenAI(
            model="meta-llama/llama-3.3-70b:free",
            openai_api_key=Config.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1"
        )

        system_prompt = f"You are Gaurav Rayat's AI agent. Use this context: {context_chunks}"
        response = llm.invoke([
            ("system", system_prompt),
            ("human", user_query)
        ])
        return response.content
    except Exception as e:
        print(f"AI error: {e}")
        return "I'm having trouble processing your request right now. Please try again later."

@bp.route("/api/ask", methods=["POST"])
def api_ask_route():
    data = request.get_json()
    user_query = data.get("question")
    
    if not user_query:
        return jsonify({"answer": "Please provide a question."}), 400
    
    answer = get_ai_answer(user_query)
    
    # Save message from API source
    save_message_to_db(
        user_message=user_query,
        ai_response=answer,
        source="api",
        user_ip=request.remote_addr
    )
    
    return jsonify({"answer": answer})
