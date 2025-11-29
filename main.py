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
    },
    {
        "url": "https://www.linkedin.com/embed/feed/update/urn:li:share:7315742381461446657?collapsed=1", 
        "title": "GATE 2025 - Data Science and Artificial Intelligence (DA)"
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

# ... (Keep your existing imports)

# --- RESUME DATA CONTEXT ---
# This gives the bot all the info it needs to answer correctly.
SYSTEM_PROMPT = """
You are the AI Assistant for Gaurav Rayat's personal portfolio. 
Your goal is to answer visitor questions professionally based on the following resume data:

**PROFILE:**
- Name: Gaurav Rayat
- Education: B.Sc. (H) Mathematics at Sri Venkateswara College, Delhi University (2026) | CGPA: 7.24
- Additional: Diploma in Data Science from IIT Madras (Pursuing) | CGPA: 8.09
- Key Achievement: Qualified GATE 2025 in Data Science & AI with All India Rank (AIR) 2177.

**EXPERIENCE:**
1. **Data Science Intern @ Intellimark.AI** (Sept-Nov 2025): Built automated time-series forecasting pipelines using SARIMA, Prophet, and XGBoost.
2. **Data Science Intern @ Unified Mentor** (Sept-Oct 2024): Developed ML models using Scikit-learn.
3. **Research Intern @ Sri Venkateswara College** (July-Sept 2024): Co-developed an NLP Chatbot using Python.
4. **Data Analyst Intern @ Studify Success** (Mar-Jun 2024): Created SQL/Python dashboards.
5. **Mathematics Trainer @ Bhanzu** (Aug-Oct 2025): Taught math to international students.
6. **Technical Team Member @ INSPIRE** (Sept 2024 - May 2025).
7. **Member @ Brainiacs Data Science Hub** (Sept 2024 - May 2025).

**PROJECTS:**
- **Spam Message Detection:** NLP web app using Streamlit & TF-IDF.
- **Iris Classification:** End-to-end ML app using SVM.
- **Telegram Chatbot:** Generative AI bot using Flask & OpenAI API.
- **Delhi Housing Price Prediction:** Regression models for property pricing.

**SKILLS:**
- Languages: Python (Advanced), SQL (Advanced).
- Libraries: Pandas, NumPy, Scikit-learn, Flask, Matplotlib.
- Tools: Power BI, Tableau, Git, Excel.

**BEHAVIOR:**
- Keep answers concise and friendly.
- If asked for contact info, provide: gaurav.rayat2004@gmail.com.
- Do not make up facts not listed here.
"""

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
        
        # Check for errors in response
        if "choices" in response_data:
            reply = response_data["choices"][0]["message"]["content"].strip()
        else:
            print("API Error:", response_data)
            reply = "I'm having trouble connecting right now. Please try again."

    except Exception as e:
        print("Server Error:", e)
        return jsonify({"response": "An internal error occurred."})

    return jsonify({"response": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))