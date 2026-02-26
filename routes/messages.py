from flask import Blueprint, request, redirect, url_for, flash
from utils.mail_helper import send_contact_email

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
