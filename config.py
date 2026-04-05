import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get("SECRET_KEY")
    
    # Session Configuration
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Mail Configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_USERNAME")
    
    # Database
    MONGO_URI = os.environ.get("MONGO_URI")
    
    # Cloudinary
    CLOUDINARY_NAME = os.environ.get("CLOUDINARY_NAME")
    CLOUDINARY_API_KEY = os.environ.get("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET")
    
    # API Keys
    OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
    TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    TELEGRAM_WEBHOOK_SECRET = os.environ.get("TELEGRAM_WEBHOOK_SECRET")
    ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH")

    # Monitoring Agent (Phase 1)
    MONITOR_TARGETS = os.environ.get(
        "MONITOR_TARGETS",
        "https://gauravrayat.me,https://gauravrayat.me/api/health"
    )
    MONITOR_TIMEOUT_SECONDS = int(os.environ.get("MONITOR_TIMEOUT_SECONDS", "10"))
    MONITOR_FAILURE_THRESHOLD = int(os.environ.get("MONITOR_FAILURE_THRESHOLD", "3"))
    MONITOR_ALERT_EMAIL = os.environ.get("MONITOR_ALERT_EMAIL", "gaurav.rayat2004@gmail.com")
    MONITOR_RUN_TOKEN = os.environ.get("MONITOR_RUN_TOKEN")
