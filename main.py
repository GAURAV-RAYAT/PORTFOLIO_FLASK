from flask import Flask, redirect, render_template, request, flash, jsonify, url_for, session, make_response
from flask_mail import Mail, Message
import requests
import os
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
import json
import cloudinary
import cloudinary.uploader
from flask import jsonify
from flask_bcrypt import Bcrypt
import fitz  # PyMuPDF
import re
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# create flask app
app = Flask(__name__)

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True, # Ensure your site has HTTPS (Vercel does this automatically)
    SESSION_COOKIE_SAMESITE='Lax',
)

# Initialize Bcrypt
bcrypt = Bcrypt(app)

# ✅ FIX: Added a fallback string so it never crashes if env var is missing
app.secret_key = os.environ.get("SECRET_KEY")

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

# --- DATABASE CONNECTION (MongoDB) ---
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

# Configure Cloudinary (Add these to Vercel Env Vars)
cloudinary.config(
  cloud_name = os.environ.get("CLOUDINARY_NAME"),
  api_key = os.environ.get("CLOUDINARY_API_KEY"),
  api_secret = os.environ.get("CLOUDINARY_API_SECRET")
)

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

    # Load LinkedIn posts from JSON
    linkedin_posts = []
    try:
        with open("data/linkedin_posts.json", "r", encoding="utf-8") as f:
            linkedin_posts = json.load(f)

        # newest first
        linkedin_posts = sorted(
            linkedin_posts,
            key=lambda x: x.get("date", ""),
            reverse=True
        )
    except Exception as e:
        print(f"LinkedIn posts load error: {e}")

    return render_template('index.html', linkedin_posts=linkedin_posts)
    
# --- SECURE AUTH HELPER ---
def is_admin():
    return session.get('log_authorized')

# --- PASSWORD MANAGER ROUTES ---
@app.route('/pass', methods=['GET', 'POST'])
def pass_manager():
    if request.method == 'POST' and 'password' in request.form:
        password = request.form.get('password')
        # Retrieve the hashed admin password from environment variables
        admin_pass_hashed = os.environ.get("ADMIN_PASSWORD_HASH")
        
        # ✅ Securely check the hashed password
        if admin_pass_hashed and bcrypt.check_password_hash(admin_pass_hashed, password):
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
            # ✅ ObjectId allows deletion to work
            pass_collection.delete_one({"_id": ObjectId(id)})
        except Exception as e:
            print(f"Delete Error: {e}")
    return redirect(url_for('pass_manager'))

# --- LOGS ROUTE (Reused Auth) ---
@app.route('/logs', methods=['GET', 'POST'])
def view_logs():
    # Handle login attempt
    if request.method == 'POST':
        password = request.form.get('password')
        # Retrieve the hash you generated earlier from your Vercel Env Vars
        admin_pass_hashed = os.environ.get("ADMIN_PASSWORD_HASH")
        
        # ✅ Use bcrypt to verify the password against the hash
        if admin_pass_hashed and bcrypt.check_password_hash(admin_pass_hashed, password):
            session['log_authorized'] = True
            return redirect(url_for('view_logs'))
        else:
            return render_template('logs.html', authenticated=False, error="Incorrect Password!")

    # Check if user is already authorized
    if not is_admin():
        return render_template('logs.html', authenticated=False)

    # Fetch logs if authorized
    logs_data = []
    if client:
        try:
            logs_data = list(visitor_collection.find().sort("_id", -1).limit(50))
        except Exception as e:
            print(f"Log Fetch Error: {e}")
    
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

def get_beautified_resume():
    pdf_path = "static/assets/RESUME.pdf"
    
    try:
        doc = fitz.open(pdf_path)
        full_text = ""
        for page in doc:
            full_text += page.get_text("text")
        
        # --- Beautification Logic ---
        # 1. Remove excessive newlines
        clean_text = re.sub(r'\n+', '\n', full_text)
        # 2. Remove multiple spaces
        clean_text = re.sub(r' +', ' ', clean_text)
        # 3. Strip whitespace from start/end
        clean_text = clean_text.strip()
        
        return clean_text
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return "Resume data currently unavailable."
    

# --- RESUME DATA CONTEXT ---
resume_context = get_beautified_resume()
SYSTEM_PROMPT = f"""
    You are the AI Assistant for Gaurav Rayat. 
    Use the following resume data to answer questions:
    
    {resume_context}
    
    Behavior: Keep answers concise and only use the provided facts.
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
            "model": "openai/gpt-4o-mini",
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

# New Route to view the document page
@app.route('/documents')
def documents_page():
    if not is_admin(): 
        return redirect(url_for('view_logs')) 
    
    # Fetch existing docs from MongoDB
    docs = []
    if client:
        docs = list(db.document_logs.find().sort("_id", -1))
    return render_template('documents.html', authenticated=True, documents=docs)

# New Route to handle the drag-and-drop upload
@app.route('/upload-doc', methods=['POST'])
def upload_document():
    if not is_admin():
        return jsonify({"error": "Unauthorized"}), 403

    file = request.files.get('file')
    if file:
        # Upload to Cloudinary
        upload_result = cloudinary.uploader.upload(file, resource_type="auto")
        file_url = upload_result.get("secure_url")

        # Save record to your existing portfolio_db
        if client:
            db.document_logs.insert_one({
                "filename": file.filename,
                "url": file_url,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        return jsonify({"url": file_url}), 200
    return "Upload failed", 400

@app.route('/delete-doc/<id>')
def delete_document(id):
    if not is_admin(): 
        return redirect(url_for('view_logs'))
    
    if client:
        try:
            # Delete record from MongoDB
            db.document_logs.delete_one({"_id": ObjectId(id)})
        except Exception as e:
            print(f"Delete Error: {e}")
            
    return redirect(url_for('documents_page'))

# -- API --
def get_trained_context():
    # This gets the absolute path to the directory where main.py sits
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    files = [
        os.path.join(base_path, "static", "assets", "RESUME.pdf"),
        os.path.join(base_path, "static", "assets", "LINKEDIN_SUMMARY.pdf")
    ]
    
    all_content = ""
    for file_path in files:
        if os.path.exists(file_path):
            try:
                loader = PyMuPDFLoader(file_path)
                docs = loader.load()
                for doc in docs:
                    all_content += doc.page_content + "\n"
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        else:
            print(f"File not found: {file_path}")
            
    return all_content

@app.route("/api/ask", methods=["POST"])
def api_ask():
    data = request.get_json()
    user_query = data.get("question")
    
    if not user_query:
        return jsonify({"error": "No question provided"}), 400

    try:
        # 1. Get the context from your PDFs
        context_chunks = get_trained_context()
        context_string = "\n".join(context_chunks)

        # 2. Use your OpenRouter API via LangChain
        # We use ChatOpenAI but point it to OpenRouter's base URL
        llm = ChatOpenAI(
            model="openai/gpt-4o-mini", # Optimized for Vercel performance
            openai_api_key=os.environ.get("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1"
        )

        system_prompt = f"You are Gaurav Rayat's AI agent. Use this context to answer: {context_string}"
        response = llm.invoke([
            ("system", system_prompt),
            ("human", user_query)
        ])

        return jsonify({"answer": response.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -- telegram--
# Add your Telegram Token from Environment Variables
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

@app.route('/api/telegram', methods=['POST'])
def telegram_webhook():
    update = request.get_json()
    
    if "message" in update and "text" in update["message"]:
        chat_id = update["message"]["chat"]["id"]
        user_text = update["message"]["text"]
        
        # 1. Get response from your existing LangChain logic
        # We reuse your get_trained_context logic here
        ai_response = api_ask(user_text) # Helper function
        
        # 2. Send the response back to Telegram
        send_message_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(send_message_url, json={
            "chat_id": chat_id,
            "text": ai_response
        })
        
    return "ok", 200

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))