from flask import Flask, render_template,request,flash, jsonify
from flask_mail import Mail, Message
import requests

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

@app.route('/')
def home():
    return render_template('index.html')  # Must be inside templates/

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
            flash("Failed to send the message. Please try again.", "danger")
    else:
        flash("All fields are required. Please fill in the form completely.", "warning")
    return render_template('index.html')

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"response": "Please enter a message."})

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-3.5-turbo",  # or try mistral/mixtral
                "messages": [
                    {"role": "system","content": ("You are an intelligent assistant on the personal portfolio website of Gaurav Rayat. Gaurav is currently pursuing a B.Sc. (Hons) in Mathematics at Sri Venkateswara College, University of Delhi with a CGPA of 7.72, and is also enrolled in the B.S. in Data Science program at IIT Madras with a CGPA of 8.09. He qualified the GATE 2025 exam in Data Science and Artificial Intelligence with an All India Rank (AIR) of 2177. He has interned as a Data Analyst at QBE Consulting and Studify Success, worked as a Data Science Intern at Unified Mentor, and contributed to chatbot development during a summer research internship at his college. Gaurav is proficient in Python, SQL, Flask, Pandas, NumPy, Scikit-learn, Seaborn, Matplotlib, Django (basic), MySQL, PostgreSQL, Git, APIs, Linux, Tableau, HTML, and CSS. His major projects include a GPT-powered Telegram chatbot, a property price prediction model for Delhi, a school management system, a diary entry manager, a crime data analyzer, and a static business website for Namrah Security. He has earned certifications in Generative AI, Business Analytics, Data Science, NLP, Machine Learning, and Python from Internshala. Gaurav is passionate about solving real-world problems using data and building intelligent systems. You must provide helpful, specific, and factual responses only based on his verified background, and avoid making assumptions. His portfolio is at https://gauravrayat.me and his GitHub is https://github.com/GAURAV-RAYAT.")},
                    {"role": "user", "content": user_message}
                ]
            }
        )
        data = response.json()
        reply = data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("OpenRouter error:", e)
        reply = "Sorry, I couldn't process your request."

    return jsonify({"response": reply})