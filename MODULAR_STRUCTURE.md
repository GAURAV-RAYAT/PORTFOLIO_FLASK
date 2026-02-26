# Modular Flask Application Structure

## Overview
Your Flask application has been refactored into a clean, modular structure following Flask best practices. This makes the code more maintainable, testable, and scalable.

## Directory Structure

```
project-root/
├── main.py                 # Application entry point and blueprint registration
├── config.py              # Centralized configuration management
├── database.py            # MongoDB connection and utilities
├── wsgi.py                # WSGI entry point for deployment
├── utils/                 # Utility modules for shared functionality
│   ├── __init__.py
│   ├── resume_parser.py   # PDF parsing and text extraction
│   ├── mail_helper.py     # Email sending utilities
│   └── geo_helper.py      # IP geolocation and visitor tracking
├── routes/                # Flask blueprints organized by feature
│   ├── __init__.py
│   ├── main_routes.py     # Home page and 404 handler
│   ├── auth.py            # Authentication, password manager, logs
│   ├── messages.py        # Contact form messaging
│   ├── chat.py            # AI chatbot endpoint
│   ├── documents.py       # Document upload/deletion
│   ├── api.py             # API endpoints for questions
│   ├── telegram.py        # Telegram bot webhook
│   └── seo.py             # SEO endpoints (robots.txt, sitemap)
├── templates/             # HTML templates
├── static/                # CSS, JS, images, PDFs
└── data/                  # Data files (LinkedIn posts, etc.)
```

## Module Descriptions

### Core Files

**main.py**
- Entry point for the Flask application
- Initializes Flask app, extensions, and configuration
- Registers all blueprints
- Imports from config, database, and routes

**config.py**
- Centralized configuration using environment variables
- All app settings in one place (session, mail, database, API keys)
- Makes it easy to manage settings across environments

**database.py**
- MongoDB connection initialization
- Database utility functions: `init_db()`, `get_db()`, `get_collection()`
- Decouples database logic from routes

### Utils Modules

**utils/resume_parser.py**
- `get_beautified_resume()` - Extracts and cleans resume PDF text
- `get_trained_context()` - Loads multiple PDFs for AI context
- PDF parsing and text preprocessing

**utils/mail_helper.py**
- `send_contact_email()` - Sends contact form emails with auto-reply
- Centralized email logic for reusability

**utils/geo_helper.py**
- `get_visitor_ip()` - Extracts visitor IP from Flask request
- `get_visitor_location()` - Fetches location data from IP
- Used by main_routes for visitor tracking

### Routes Modules (Blueprints)

**routes/main_routes.py**
- `@bp.route('/')` - Home page with visitor logging
- `@bp.route('/logout')` - Logout functionality
- `@bp.errorhandler(404)` - Custom 404 page

**routes/auth.py**
- `is_admin()` - Session auth helper
- `@bp.route('/pass')` - Password manager (GET/POST)
- `@bp.route('/add_pass')` - Add password entry
- `@bp.route('/delete_pass/<id>')` - Delete password
- `@bp.route('/logs')` - View visitor logs
- All routes share the same password authentication mechanism

**routes/messages.py**
- `@bp.route('/send_messege')` - Handle contact form submission
- Uses mail_helper for email sending

**routes/chat.py**
- `@bp.route('/chat')` - AI chatbot endpoint
- Uses OpenRouter API with resume context
- Resume data loaded once at startup

**routes/documents.py**
- `@bp.route('/documents')` - View uploaded documents
- `@bp.route('/upload-doc')` - Upload file to Cloudinary
- `@bp.route('/delete-doc/<id>')` - Delete document

**routes/api.py**
- `get_ai_answer()` - Shared AI logic for API and Telegram
- `@bp.route('/api/ask')` - API endpoint for asking questions
- Uses trained context from PDFs

**routes/telegram.py**
- `@bp.route('/api/telegram')` - Telegram bot webhook
- Reuses `get_ai_answer()` from api.py module

**routes/seo.py**
- `@bp.route('/robots.txt')` - Robots file
- `@bp.route('/sitemap.xml')` - XML sitemap

## Benefits of This Structure

1. **Separation of Concerns** - Each module has a single responsibility
2. **Code Reusability** - Utilities are imported where needed (e.g., `get_ai_answer()`)
3. **Easier Testing** - Functions and blueprints can be tested in isolation
4. **Scalability** - Easy to add new routes or features
5. **Maintainability** - Find and modify code quickly
6. **Configuration Management** - All settings in one place
7. **Import Clarity** - Each file clearly shows its dependencies

## Adding New Features

### Adding a New Route
1. Create a new file in `routes/new_feature.py`
2. Define a blueprint: `bp = Blueprint('new_feature', __name__)`
3. Add your routes as methods on the blueprint
4. Import and register in `main.py`: `app.register_blueprint(bp)`

### Adding Helper Functions
1. Create a new file in `utils/`
2. Define your utility functions
3. Import in routes/modules that need them

### Adding Configuration
1. Add new environment variable in `config.py`
2. Reference via `Config.VARIABLE_NAME`

## Running the Application

```bash
# Development
python main.py

# Production (Vercel)
# Uses wsgi.py as entry point
```

## Environment Variables

All environment variables are defined in `config.py`. Required variables:
- `SECRET_KEY` - Flask session key
- `MONGO_URI` - MongoDB connection string
- `MAIL_USERNAME` / `MAIL_PASSWORD` - Gmail credentials
- `CLOUDINARY_*` - Cloudinary API credentials
- `OPENROUTER_API_KEY` - OpenRouter API key
- `TELEGRAM_BOT_TOKEN` - Telegram bot token
- `ADMIN_PASSWORD_HASH` - Bcrypt hash of admin password
