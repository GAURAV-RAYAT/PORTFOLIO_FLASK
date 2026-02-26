from flask import Blueprint, render_template, request, redirect, url_for, session
from datetime import datetime
import json
from database import get_collection, get_client
from utils.geo_helper import get_visitor_ip, get_visitor_location

bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    # 1. Get Visitor IP
    visitor_ip = get_visitor_ip(request)

    # 2. Get Location & Save to DB
    try:
        loc_data = get_visitor_location(visitor_ip)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # --- LOG TO MONGODB ---
        if get_client():
            log_entry = {
                "ip": visitor_ip,
                "city": loc_data["city"],
                "country": loc_data["country"],
                "isp": loc_data["isp"],
                "timestamp": timestamp
            }
            visitor_collection = get_collection("visitor_logs")
            visitor_collection.insert_one(log_entry)
            print(f"✅ Saved to DB: {loc_data['city']}, {loc_data['country']}")
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


@bp.route('/logout')
def logout():
    session.pop('log_authorized', None)
    return redirect(url_for('main.home'))


@bp.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
