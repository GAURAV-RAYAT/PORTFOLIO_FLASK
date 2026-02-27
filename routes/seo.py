from flask import Blueprint, make_response
from datetime import datetime

bp = Blueprint('seo', __name__)

@bp.route('/robots.txt')
def robots():
    # Enhanced robots.txt with crawl optimization
    content = """User-agent: *
Allow: /
Disallow: /admin/
Disallow: /__pycache__/
Disallow: /.git/
Disallow: /node_modules/
Disallow: /venv/

Sitemap: https://gauravrayat.me/sitemap.xml
Sitemap: https://gauravrayat.me/sitemap-index.xml

User-agent: Googlebot
Allow: /
Crawl-delay: 0

User-agent: Bingbot
Allow: /
Crawl-delay: 1
"""
    response = make_response(content)
    response.headers["Content-Type"] = "text/plain"
    return response

@bp.route('/sitemap.xml')
def sitemap():
    """Main sitemap with high-priority pages"""
    lastmod_date = datetime.now().strftime("%Y-%m-%d")
    
    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"
        xmlns:mobile="http://www.google.com/schemas/sitemap-mobile/1.0">
    <!-- Homepage -->
    <url>
        <loc>https://gauravrayat.me/</loc>
        <lastmod>{lastmod_date}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>1.0</priority>
        <image:image>
            <image:loc>https://gauravrayat.me/static/assets/images/my-avatar.png</image:loc>
            <image:title>Gaurav Rayat - Data Scientist Portfolio</image:title>
        </image:image>
        <mobile:mobile/>
    </url>
    
    <!-- Portfolio Page -->
    <url>
        <loc>https://gauravrayat.me/#portfolio</loc>
        <lastmod>{lastmod_date}</lastmod>
        <changefreq>bi-weekly</changefreq>
        <priority>0.9</priority>
    </url>
    
    <!-- Resume Page -->
    <url>
        <loc>https://gauravrayat.me/#resume</loc>
        <lastmod>{lastmod_date}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.85</priority>
    </url>
    
    <!-- Contact Page -->
    <url>
        <loc>https://gauravrayat.me/#contact</loc>
        <lastmod>{lastmod_date}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>
    
    <!-- Password Generator -->
    <url>
        <loc>https://gauravrayat.me/pass</loc>
        <lastmod>{lastmod_date}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.5</priority>
    </url>
    
    <!-- External Project Links -->
    <url>
        <loc>https://irisflowerclassification-nrvu9opgqoeumpd6shav6y.streamlit.app/</loc>
        <lastmod>{lastmod_date}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.7</priority>
    </url>
    
    <url>
        <loc>https://spamdetection-mue3rguqznuqyb2zkweuds.streamlit.app/</loc>
        <lastmod>{lastmod_date}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.7</priority>
    </url>
    
    <url>
        <loc>https://calc.gauravrayat.me</loc>
        <lastmod>{lastmod_date}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.6</priority>
    </url>
    
    <url>
        <loc>https://namrah.gauravrayat.me</loc>
        <lastmod>{lastmod_date}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.6</priority>
    </url>
    
    <url>
        <loc>https://dairy.gauravrayat.me</loc>
        <lastmod>{lastmod_date}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.6</priority>
    </url>
    
    <url>
        <loc>https://crime.gauravrayat.me</loc>
        <lastmod>{lastmod_date}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.6</priority>
    </url>
    
    <url>
        <loc>https://school.gauravrayat.me</loc>
        <lastmod>{lastmod_date}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.6</priority>
    </url>
</urlset>"""
    
    response = make_response(content)
    response.headers["Content-Type"] = "application/xml"
    return response

@bp.route('/sitemap-index.xml')
def sitemap_index():
    """Sitemap index for multiple sitemaps"""
    content = """<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <sitemap>
        <loc>https://gauravrayat.me/sitemap.xml</loc>
    </sitemap>
</sitemapindex>"""
    
    response = make_response(content)
    response.headers["Content-Type"] = "application/xml"
    return response
