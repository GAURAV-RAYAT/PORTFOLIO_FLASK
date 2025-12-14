from flask import Flask, redirect, render_template, request, flash, jsonify, url_for, session, make_response
from flask_mail import Mail, Message
import requests
import os
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId

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
        db = client.get_database("portfolio_db")
        visitor_collection = db.visitor_logs
        message_collection = db.messages
        pass_collection = db.passwords
        print("✅ Connected to MongoDB!")
    else:
        client = None
        print("⚠️ MONGO_URI not found.")
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
# --- SECURE AUTH HELPER ---
def is_admin():
    return session.get('log_authorized')

# --- PASSWORD MANAGER ROUTES ---
@app.route('/pass', methods=['GET', 'POST'])
def pass_manager():
    # Login Logic
    if request.method == 'POST' and 'password' in request.form:
        password = request.form.get('password')
        admin_pass = os.environ.get("ADMIN_PASSWORD", "admin123")
        if password == admin_pass:
            session['log_authorized'] = True
            return redirect(url_for('pass_manager'))
        else:
            return render_template('passwords.html', authenticated=False, error="Incorrect Password!")

    if not is_admin():
        return render_template('passwords.html', authenticated=False)

    passwords = []
    if client:
        try:
            passwords = list(pass_collection.find().sort("_id", -1))
        except Exception as e:
            print(f"DB Error: {e}")

    return render_template('passwords.html', authenticated=True, passwords=passwords)

@app.route('/add_pass', methods=['POST'])
def add_pass():
    if not is_admin(): return redirect(url_for('pass_manager'))
    
    custom_id = request.form.get('custom_id')
    password_val = request.form.get('password_val')
    comment = request.form.get('comment')
    
    if client and custom_id and password_val:
        pass_collection.insert_one({
            "custom_id": custom_id,
            "password": password_val,
            "comment": comment
        })
    return redirect(url_for('pass_manager'))

@app.route('/delete_pass/<id>')
def delete_pass(id):
    if not is_admin(): return redirect(url_for('pass_manager'))
    if client:
        try:
            # ✅ FIXED: ObjectId allows deletion to work
            pass_collection.delete_one({"_id": ObjectId(id)})
        except Exception as e:
            print(f"Delete Error: {e}")
    return redirect(url_for('pass_manager'))

# --- LOGS ROUTE (Reused Auth) ---
@app.route('/logs', methods=['GET', 'POST'])
def view_logs():
    if request.path == '/logout':
        session.pop('log_authorized', None)
        return redirect(url_for('home'))

    if request.method == 'POST':
        password = request.form.get('password')
        admin_pass = os.environ.get("ADMIN_PASSWORD", "admin123") 
        if password == admin_pass:
            session['log_authorized'] = True
            return redirect(url_for('view_logs'))

    if not is_admin():
        return render_template('logs.html', authenticated=False)

    logs_data = []
    if client:
        try:
            logs_data = list(visitor_collection.find().sort("_id", -1).limit(50))
        except Exception: pass
    
    return render_template('logs.html', authenticated=True, logs=logs_data)

@app.route('/logout')
def logout():
    session.pop('log_authorized', None)
    return redirect(url_for('home'))

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


@app.route('/robots.txt')
def robots():
    content = "User-agent: *\nAllow: /\nSitemap: https://gauravrayat.me/sitemap.xml"
    response = make_response(content)
    response.headers["Content-Type"] = "text/plain"
    return response

@app.route('/sitemap.xml')
def sitemap():
    # Update this date to the current date whenever you make major changes
    lastmod_date = datetime.now().strftime("%Y-%m-%d")
    
    content = f"""<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url>
            <loc>https://gauravrayat.me/</loc>
            <lastmod>{lastmod_date}</lastmod>
            <priority>1.0</priority>
        </url>
        <url>
            <loc>https://gauravrayat.me/pass</loc>
            <priority>0.1</priority>
        </url>
    </urlset>"""
    
    response = make_response(content)
    response.headers["Content-Type"] = "application/xml"
    return response

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))