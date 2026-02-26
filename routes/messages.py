from flask import Blueprint, request, redirect, url_for, flash, render_template, jsonify
from utils.mail_helper import send_contact_email
from database import get_collection

bp = Blueprint('messages', __name__)

@bp.route('/send_messege', methods=['POST'])
def send_message():
    fullname = request.form.get('fullname')
    email = request.form.get('email')
    message_content = request.form.get('message')

    if fullname and email and message_content:
        success, message = send_contact_email(fullname, email, message_content)
        flash(message, "success" if success else "error")
    else:
        flash("All fields are required.", "warning")
    
    return redirect(url_for('main.home'))


@bp.route('/ai-messages', methods=['GET'])
def view_ai_messages():
    """Display all AI messages"""
    print("🔍 /ai-messages route accessed!")
    
    try:
        chat_collection = get_collection("ai_messages")
        print(f"✅ Chat collection: {chat_collection}")
        
        if chat_collection is None:
            print("❌ Chat collection is None")
            messages = []
        else:
            # Get all messages sorted by most recent first
            messages = list(chat_collection.find().sort("timestamp", -1))
            print(f"✅ Found {len(messages)} messages")
            
            # Format timestamps for display
            for msg in messages:
                if 'timestamp' in msg:
                    msg['formatted_time'] = msg['timestamp'].strftime("%B %d, %Y at %I:%M %p")
        
        print(f"📋 Rendering with {len(messages)} messages")
        return render_template('ai_messages.html', messages=messages)
        
    except Exception as e:
        print(f"❌ Error fetching messages: {e}")
        import traceback
        traceback.print_exc()
        messages = []
        return render_template('ai_messages.html', messages=messages)
