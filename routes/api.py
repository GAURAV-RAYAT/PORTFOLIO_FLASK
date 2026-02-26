from flask import Blueprint, request, jsonify
from langchain_openai import ChatOpenAI
from config import Config
from utils.resume_parser import get_trained_context

bp = Blueprint('api', __name__)

def get_ai_answer(user_query):
    """Shared logic for API and Telegram."""
    try:
        # 1. Get the context from PDFs
        context_chunks = get_trained_context()

        # 2. Setup LLM
        llm = ChatOpenAI(
            model="openai/gpt-4o-mini",
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
        return f"Error: {str(e)}"

@bp.route("/api/ask", methods=["POST"])
def api_ask_route():
    data = request.get_json()
    user_query = data.get("question")
    
    if not user_query:
        return jsonify({"answer": "Please provide a question."}), 400
    
    answer = get_ai_answer(user_query)
    return jsonify({"answer": answer})
