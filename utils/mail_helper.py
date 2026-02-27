from flask_mail import Message
from flask import current_app
from datetime import datetime

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


def send_ai_message_notification_email(user_message, ai_response, source="web", telegram_user_id=None, user_ip=""):
    """Send email notification whenever AI is asked a question from any source"""
    try:
        # Determine source label and icon
        source_info = {
            "web": {"label": "Web Chat", "icon": "💻"},
            "telegram": {"label": "Telegram", "icon": "📱"},
            "api": {"label": "API", "icon": "🔌"}
        }
        
        source_data = source_info.get(source, {"label": "Unknown", "icon": "❓"})
        
        # Build email body
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        
        # Build source info with conditional fields
        source_info_html = f"""
        <p style="margin: 0; color: #666;"><strong>Source:</strong> {source_data['icon']} {source_data['label']}</p>
        <p style="margin: 5px 0 0 0; color: #666;"><strong>Time:</strong> {timestamp}</p>
        """
        
        if telegram_user_id:
            source_info_html += f"<p style=\"margin: 5px 0 0 0; color: #666;\"><strong>Telegram User ID:</strong> {telegram_user_id}</p>"
        
        if user_ip:
            source_info_html += f"<p style=\"margin: 5px 0 0 0; color: #666;\"><strong>IP Address:</strong> {user_ip}</p>"
        
        email_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <h2 style="color: #1e3c72; margin-bottom: 20px;">🤖 New AI Message Notification</h2>
                    
                    <div style="background-color: #f9f9f9; padding: 15px; border-left: 4px solid #4dd0e1; margin-bottom: 20px;">
                        {source_info_html}
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <h3 style="color: #ff9800; margin-bottom: 10px;">👤 User Question:</h3>
                        <p style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; color: #333; line-height: 1.6;">{user_message}</p>
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <h3 style="color: #2196f3; margin-bottom: 10px;">🤖 AI Response:</h3>
                        <p style="background-color: #e3f2fd; padding: 15px; border-radius: 5px; color: #333; line-height: 1.6;">{ai_response}</p>
                    </div>
                    
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                    
                    <div style="text-align: center; color: #999; font-size: 12px;">
                        <p>This is an automated notification from your AI chatbot system.</p>
                        <p><a href="https://gauravrayat.me/ai-messages" style="color: #4dd0e1; text-decoration: none;">View all messages</a></p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        # Create and send email
        msg = Message(
            subject=f"🤖 AI Message Notification - {source_data['label']} | gauravrayat.me",
            sender=current_app.config['MAIL_USERNAME'],
            recipients=["gaurav.rayat2004@gmail.com"],
            html=email_body
        )
        current_app.extensions['mail'].send(msg)
        print(f"✅ AI message notification email sent for {source} query!")
        return True
    
    except Exception as e:
        print(f"❌ Error sending AI message notification email: {e}")
        import traceback
        traceback.print_exc()
        return False
