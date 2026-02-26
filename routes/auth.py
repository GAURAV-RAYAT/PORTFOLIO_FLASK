from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_bcrypt import Bcrypt
from bson.objectid import ObjectId
from config import Config
from database import get_collection, get_client

bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

# --- SECURE AUTH HELPER ---
def is_admin():
    return session.get('log_authorized')

# --- PASSWORD MANAGER ROUTES ---
@bp.route('/pass', methods=['GET', 'POST'])
def pass_manager():
    if request.method == 'POST' and 'password' in request.form:
        password = request.form.get('password')
        
        # ✅ Securely check the hashed password
        if Config.ADMIN_PASSWORD_HASH and bcrypt.check_password_hash(Config.ADMIN_PASSWORD_HASH, password):
            session['log_authorized'] = True
            return redirect(url_for('auth.pass_manager'))
        else:
            return render_template('passwords.html', authenticated=False, error="Incorrect Password!")

    if not is_admin():
        return render_template('passwords.html', authenticated=False)

    passwords = []
    if get_client() is not None:
        try:
            pass_collection = get_collection("passwords")
            passwords = list(pass_collection.find().sort("_id", -1))
        except Exception as e:
            print(f"DB Error: {e}")

    return render_template('passwords.html', authenticated=True, passwords=passwords)

@bp.route('/add_pass', methods=['POST'])
def add_pass():
    if not is_admin(): 
        return redirect(url_for('auth.pass_manager'))
    
    custom_id = request.form.get('custom_id')
    password_val = request.form.get('password_val')
    comment = request.form.get('comment')
    
    if get_client() is not None and custom_id and password_val:
        pass_collection = get_collection("passwords")
        pass_collection.insert_one({
            "custom_id": custom_id,
            "password": password_val,
            "comment": comment
        })
    return redirect(url_for('auth.pass_manager'))

@bp.route('/delete_pass/<id>')
def delete_pass(id):
    if not is_admin(): 
        return redirect(url_for('auth.pass_manager'))
    
    if get_client() is not None:
        try:
            pass_collection = get_collection("passwords")
            pass_collection.delete_one({"_id": ObjectId(id)})
        except Exception as e:
            print(f"Delete Error: {e}")
    
    return redirect(url_for('auth.pass_manager'))

# --- LOGS ROUTE (Reused Auth) ---
@bp.route('/logs', methods=['GET', 'POST'])
def view_logs():
    # Handle login attempt
    if request.method == 'POST':
        password = request.form.get('password')
        
        # ✅ Use bcrypt to verify the password against the hash
        if Config.ADMIN_PASSWORD_HASH and bcrypt.check_password_hash(Config.ADMIN_PASSWORD_HASH, password):
            session['log_authorized'] = True
            return redirect(url_for('auth.view_logs'))
        else:
            return render_template('logs.html', authenticated=False, error="Incorrect Password!")

    # Check if user is already authorized
    if not is_admin():
        return render_template('logs.html', authenticated=False)

    # Fetch logs if authorized
    logs_data = []
    if get_client() is not None:
        try:
            visitor_collection = get_collection("visitor_logs")
            logs_data = list(visitor_collection.find().sort("_id", -1).limit(50))
        except Exception as e:
            print(f"Log Fetch Error: {e}")
    
    return render_template('logs.html', authenticated=True, logs=logs_data)

@bp.route('/logout')
def logout():
    session.pop('log_authorized', None)
    return redirect(url_for('main.home'))
