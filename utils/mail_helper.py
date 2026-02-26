from flask_mail import Message
from flask import current_app

def send_contact_email(fullname, email, message_content):
    """Send contact form message and auto-reply"""
    try:
        msg = Message(
            subject=f"Contact Form Message from {fullname} | gauravrayat.me",
            sender=email,
            recipients=["gaurav.rayat2004@gmail.com"],
            body=f"Name: {fullname}\nEmail: {email}\nMessage: {message_content}"
        )
        current_app.extensions['mail'].send(msg)

        auto_reply = Message(
            subject="Thank you for contacting me! | Gaurav Rayat",
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[email],
            body=f"Hi {fullname},\n\nThank you for reaching out! I have received your message and will get back to you as soon as possible.\n\nBest regards,\nGaurav Rayat"
        )
        current_app.extensions['mail'].send(auto_reply)
        return True, "Your message has been sent successfully!"
    
    except Exception as e:
        print(f"Email Error: {e}")
        return False, "Failed to send message. Please try again."
