from flask import Flask, render_template, request, flash, jsonify
from flask_mail import Mail, Message
import requests
import os

# create flask app
app = Flask(__name__)
app.secret_key = "c996df478d4c087e03029a962b7f016e"
OPENROUTER_API_KEY = "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"

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = "gaurav.rayat2004@gmail.com"
app.config['MAIL_PASSWORD'] = "qrcdulgqqyrxdwuk"
app.config['MAIL_DEFAULT_SENDER'] = "gaurav.rayat2004@gmail.com"
mail = Mail(app)

# --- LINKEDIN CONFIGURATION ---
# Since we don't have a Company Page, we use this list.
# To update your site, just add your new LinkedIn Post URL here.
LINKEDIN_POSTS = [
    {
        "url": "https://www.linkedin.com/embed/feed/update/urn:li:share:7376244294661124096?collapsed=1", 
        "title": "AI in Medical Imaging: Revolutionizing Healthcare with Deep Learning"
    },
    {
        "url": "https://www.linkedin.com/embed/feed/update/urn:li:share:7351984929309671424?collapsed=1", 
        "title": "Internship Experience at QBE Consulting"
    }
]

@app.route('/')
def home():
    # We pass the posts to the template
    return render_template('index.html', linkedin_posts=LINKEDIN_POSTS)

@app.route('/send_messege', methods=['POST'])
def send_message():
    fullname = request.form.get('fullname')
    email = request.form.get('email')
    message_content = request.form.get('message')

    if fullname and email and message_content:
        try:
            msg = Message(
                subject=f"Contact Form Message from {fullname}",
                sender=email,
                recipients=["gaurav.rayat2004@gmail.com", "1722024@svc.du.ac.in"],
                body=f"Name: {fullname}\nEmail: {email}\nMessage: {message_content}"
            )
            mail.send(msg)
            flash("Your message has been sent successfully!", "success")
        except Exception as e:
            flash("Failed to send the message.", "danger")
    else:
        flash("All fields are required.", "warning")
    return render_template('index.html', linkedin_posts=LINKEDIN_POSTS)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"response": "Please enter a valid message."})

    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are Gaurav Rayat's portfolio assistant."},
                {"role": "user", "content": user_message}
            ]
        }
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        reply = response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return jsonify({"response": "An error occurred."})

    return jsonify({"response": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))