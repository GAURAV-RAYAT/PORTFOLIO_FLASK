from flask import Flask, render_template,request,flash
from flask_mail import Mail, Message

# create flask app
app = Flask(__name__)
app.secret_key = "c996df478d4c087e03029a962b7f016e"

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