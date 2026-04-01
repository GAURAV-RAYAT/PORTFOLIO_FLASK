from flask import Flask
from flask_mail import Mail
from flask_bcrypt import Bcrypt
import cloudinary
from config import Config
from database import init_db
from routes.auth import bp as auth_bp, bcrypt as auth_bcrypt
from routes.main_routes import bp as main_bp
from routes.messages import bp as messages_bp
from routes.chat import bp as chat_bp
from routes.documents import bp as documents_bp
from routes.api import bp as api_bp
from routes.telegram import bp as telegram_bp
from routes.seo import bp as seo_bp
from routes.monitoring import bp as monitoring_bp

# Create Flask app
app = Flask(__name__)

# Load configuration
app.config.from_object(Config)

# SEO and Security Headers
@app.after_request
def add_seo_headers(response):
    """Add SEO and security headers to all responses"""
    # Security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=(), payment=()'
    
    # SEO headers
    response.headers['Content-Language'] = 'en'
    
    # Caching headers for static content
    if response.mimetype and response.mimetype.startswith('image/'):
        response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
    elif response.mimetype in ['text/css', 'application/javascript', 'text/javascript']:
        response.headers['Cache-Control'] = 'public, max-age=2592000, immutable'
    else:
        response.headers['Cache-Control'] = 'public, max-age=3600, must-revalidate'
    
    return response

# Initialize extensions
mail = Mail(app)
bcrypt = Bcrypt(app)
auth_bcrypt.init_app(app)

# Initialize Cloudinary
cloudinary.config(
    cloud_name=Config.CLOUDINARY_NAME,
    api_key=Config.CLOUDINARY_API_KEY,
    api_secret=Config.CLOUDINARY_API_SECRET
)

# Initialize Database
init_db()

# Register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(messages_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(documents_bp)
app.register_blueprint(api_bp)
app.register_blueprint(telegram_bp)
app.register_blueprint(seo_bp)
app.register_blueprint(monitoring_bp)

if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
