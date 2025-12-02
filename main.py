from flask import Flask, redirect, render_template, request, flash, jsonify, url_for, session
from flask_mail import Mail, Message
import requests
import os
from datetime import datetime
from pymongo import MongoClient

# create flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

# --- DATABASE CONNECTION (MongoDB) ---
# We get the connection string from Vercel Environment Variables
MONGO_URI = os.environ.get("MONGO_URI")
try:
    if MONGO_URI:
        client = MongoClient(MONGO_URI)
        db = client.get_database("portfolio_db") # Database Name
        visitor_collection = db.visitor_logs     # Collection Name
        print("✅ Connected to MongoDB!")
    else:
        client = None
        print("⚠️ MONGO_URI not found. Database logging disabled.")
except Exception as e:
    client = None
    print(f"❌ Database Connection Error: {e}")

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']
mail = Mail(app)

# --- LINKEDIN POSTS ---
LINKEDIN_POSTS = [
    {
        "url": "https://www.linkedin.com/embed/feed/update/urn:li:share:7401467953118179329?collapsed=1", 
        "title": "I love delhi, but soul belongs to Himachal."
    },
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
    # 1. Get Visitor IP
    if request.headers.getlist("X-Forwarded-For"):
        visitor_ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        visitor_ip = request.remote_addr

    # 2. Get Location & Save to DB
    try:
        # Fetch location details
        response = requests.get(f"http://ip-api.com/json/{visitor_ip}")
        loc_data = response.json()
        city = loc_data.get("city", "Unknown City")
        country = loc_data.get("country", "Unknown Country")
        isp = loc_data.get("isp", "Unknown ISP")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # --- LOG TO MONGODB ---
        if client:
            log_entry = {
                "ip": visitor_ip,
                "city": city,
                "country": country,
                "isp": isp,
                "timestamp": timestamp
            }
            visitor_collection.insert_one(log_entry)
            print(f"✅ Saved to DB: {city}, {country}")
        else:
            print("⚠️ Database not connected. Log skipped.")
        
    except Exception as e:
        print(f"Visitor Tracking Error: {e}")

    return render_template('index.html', linkedin_posts=LINKEDIN_POSTS)

# --- SECURE LOGS ROUTE ---
@app.route('/logs', methods=['GET', 'POST'])
def view_logs():
    # 1. Handle Logout Logic if accessed via /logout
    if request.path == '/logout':
        session.pop('log_authorized', None)
        return redirect(url_for('home'))

    # 2. Handle Password Submission
    error = None
    if request.method == 'POST':
        password = request.form.get('password')
        # Check against Environment Variable (or hardcoded for now)
        admin_pass = os.environ.get("ADMIN_PASSWORD", "admin123") 
        
        if password == admin_pass:
            session['log_authorized'] = True
            return redirect(url_for('view_logs'))
        else:
            error = "Incorrect Password!"

    # 3. Check Authorization
    if not session.get('log_authorized'):
        return render_template('logs.html', authenticated=False, error=error)

    # 4. Fetch Logs if Authorized
    logs_data = []
    if client:
        try:
            # Fetch last 50 logs, sorted by newest first
            cursor = visitor_collection.find().sort("_id", -1).limit(50)
            logs_data = list(cursor)
        except Exception as e:
            print(f"DB Error: {e}")
    
    return render_template('logs.html', authenticated=True, logs=logs_data)

@app.route('/logout')
def logout():
    session.pop('log_authorized', None)
    return redirect(url_for('view_logs'))

@app.route('/send_messege', methods=['POST'])
def send_message():
    fullname = request.form.get('fullname')
    email = request.form.get('email')
    message_content = request.form.get('message')

    if fullname and email and message_content:
        try:
            msg = Message(
                subject=f"Contact Form Message from {fullname} | gauravrayat.me",
                sender=email,
                recipients=["gaurav.rayat2004@gmail.com"],
                body=f"Name: {fullname}\nEmail: {email}\nMessage: {message_content}"
            )
            mail.send(msg)

            auto_reply = Message(
                subject="Thank you for contacting me! | Gaurav Rayat",
                sender=app.config['MAIL_USERNAME'],
                recipients=[email],
                body=f"Hi {fullname},\n\nThank you for reaching out! I have received your message and will get back to you as soon as possible.\n\nBest regards,\nGaurav Rayat"
            )
            mail.send(auto_reply)

            flash("Your message has been sent successfully!", "success")
        except Exception as e:
            pass
    else:
        flash("All fields are required.", "warning")
    return redirect(url_for('home'))

# --- RESUME DATA CONTEXT ---
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