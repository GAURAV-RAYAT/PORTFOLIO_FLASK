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
                "model": "openai/gpt-3.5-turbo",
                "messages": [
                    {"role": "system","content": ("Gaurav Rayat is a dedicated and passionate individual pursuing a B.Sc. (Hons) in Mathematics at Sri Venkateswara College, University of Delhi, and a BS in Data Science through an online program at IIT Madras, demonstrating a strong academic foundation with a CGPA of 7.72 in Mathematics and 8.09 in Data Science. He has achieved significant academic milestones, including qualifying GATE 2025 in Data Science and Artificial Intelligence with an impressive All India Rank (AIR) of 2177. Known for his ability to transform raw data into actionable insights, Gaurav specializes in leveraging tools and techniques like Python, SQL, and advanced machine learning algorithms to solve complex problems. His academic journey reflects consistent excellence, having completed Class XII from Deepalaya School in South Delhi with 91.6% and Class X with 87.6%. Professionally, he has gained substantial experience through internships and research roles, including automating workflows and creating advanced dashboards using Python and MySQL as a Data Analyst Intern at QBE Consulting, developing end-to-end machine learning models and improving their accuracy with Scikit-learn during his Data Science Internship at Unified Mentor, designing NLP-powered chatbots for real-time user interactions as a Chatbot Development Intern at Sri Venkateswara College, and integrating Python and Tableau to deliver data-driven insights as a Data Analyst Intern at Studify Success. His technical expertise spans programming languages like Python, SQL, and R, libraries such as NumPy, Pandas, and Scikit-learn, and tools like MySQL, PostgreSQL, Tableau, Power BI, Git, and Linux, underscoring his proficiency in machine learning, exploratory data analysis, and neural networks. Among his key projects are the development of a GPT-powered AI conversational bot for Telegram, enabling human-like interactions; a Housing Price Prediction model leveraging machine learning to forecast property prices in Delhi; and a professional website for Namrah Group of Security, showcasing his web development skills. Gaurav’s commitment to continuous learning is reflected in his certifications in Generative AI, Business Analytics, Python Programming, and Data Science from Internshala, and his dedication has been recognized through numerous accolades, including the Young Scientist Award, Tata Capital Pankh Scholarship, and Hana Nanum Scholarship. With a vision to leverage data science and artificial intelligence to create meaningful solutions for real-world problems, Gaurav values innovation, collaboration, and adaptability, aspiring to make impactful contributions to analytics and AI while driving change and delivering value through data-driven insights. For more information, his portfolio is available at gauravrayat.me, and he can be contacted via email at gaurav.rayat2004@gmail.com or phone at +91 9560320313.")},
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