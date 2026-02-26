from flask import Blueprint, make_response
from datetime import datetime

bp = Blueprint('seo', __name__)

@bp.route('/robots.txt')
def robots():
    content = "User-agent: *\nAllow: /\nSitemap: https://gauravrayat.me/sitemap.xml"
    response = make_response(content)
    response.headers["Content-Type"] = "text/plain"
    return response

@bp.route('/sitemap.xml')
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
