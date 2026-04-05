from flask import Blueprint, make_response

bp = Blueprint('seo', __name__)

# Fixed lastmod date — update this manually when you deploy significant changes
SITE_LASTMOD = "2026-04-02"

@bp.route('/robots.txt')
def robots():
    content = """User-agent: *
Allow: /
Disallow: /pass
Disallow: /logs
Disallow: /documents
Disallow: /ai-messages
Disallow: /add_pass
Disallow: /delete_pass/
Disallow: /upload-doc
Disallow: /delete-doc/
Disallow: /admin/
Disallow: /__pycache__/
Disallow: /.git/

Sitemap: https://gauravrayat.me/sitemap.xml

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
    """Main sitemap — only pages on gauravrayat.me; no hash anchors or external URLs"""
    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
    <!-- Homepage (single-page app; all sections live here) -->
    <url>
        <loc>https://gauravrayat.me/</loc>
        <lastmod>{SITE_LASTMOD}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>1.0</priority>
        <image:image>
            <image:loc>https://gauravrayat.me/static/assets/images/my-avatar.png</image:loc>
            <image:title>Gaurav Rayat - Data Scientist Portfolio</image:title>
        </image:image>
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

