from flask import Blueprint, render_template, request, redirect, url_for, session
from datetime import datetime, timezone
import json
import os
import threading
from database import get_collection, get_client
from utils.geo_helper import get_visitor_ip, get_visitor_location

bp = Blueprint('main', __name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _log_visitor(visitor_ip):
    """Run geo-lookup and DB insert in a background thread to avoid blocking the response."""
    try:
        loc_data = get_visitor_location(visitor_ip)
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        if get_client() is not None:
            log_entry = {
                "ip": visitor_ip,
                "city": loc_data["city"],
                "country": loc_data["country"],
                "isp": loc_data["isp"],
                "timestamp": timestamp
            }
            visitor_collection = get_collection("visitor_logs")
            visitor_collection.insert_one(log_entry)
    except Exception as e:
        print(f"Visitor Tracking Error: {e}")


@bp.route('/')
def home():
    visitor_ip = get_visitor_ip(request)
    threading.Thread(target=_log_visitor, args=(visitor_ip,), daemon=True).start()

    # Load LinkedIn posts from JSON using absolute path
    linkedin_posts = []
    try:
        posts_path = os.path.join(BASE_DIR, "data", "linkedin_posts.json")
        with open(posts_path, "r", encoding="utf-8") as f:
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


@bp.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
