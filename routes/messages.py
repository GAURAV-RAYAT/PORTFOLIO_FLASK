from flask import Blueprint, request, redirect, url_for, flash, render_template
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
    try:
        chat_collection = get_collection("ai_messages")
        if chat_collection:
            # Get all messages sorted by most recent first
            messages = list(chat_collection.find().sort("timestamp", -1))
            
            # Format timestamps for display
            for msg in messages:
                if 'timestamp' in msg:
                    msg['formatted_time'] = msg['timestamp'].strftime("%B %d, %Y at %I:%M %p")
            
            return render_template('ai_messages.html', messages=messages)
        else:
            flash("Database connection error.", "error")
            return redirect(url_for('main.home'))
    except Exception as e:
        print(f"Error fetching messages: {e}")
        flash("Error fetching messages.", "error")
        return redirect(url_for('main.home'))
