from playwright.sync_api import sync_playwright
import json
from datetime import datetime
import os

LINKEDIN_PROFILE_URL = "https://www.linkedin.com/in/gaurav-rayat/"

DATA_FILE = "data/linkedin_posts.json"
COOKIE_FILE = "linkedin_cookies.json"

def load_existing_posts():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_posts(posts):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)

def normalize_cookies(cookies):
    normalized = []
    for c in cookies:
        cookie = {
            "name": c.get("name"),
            "value": c.get("value"),
            "domain": c.get("domain", ".linkedin.com"),
            "path": c.get("path", "/"),
            "secure": c.get("secure", True),
            "httpOnly": c.get("httpOnly", False),
        }

        same_site = c.get("sameSite", "None")
        if same_site not in ("Strict", "Lax", "None"):
            same_site = "None"

        cookie["sameSite"] = same_site
        normalized.append(cookie)

    return normalized

def run():
    existing_posts = load_existing_posts()
    existing_urls = {p["url"] for p in existing_posts}

    cookie_data = os.environ.get("LINKEDIN_COOKIES")

    if cookie_data:
        cookies = json.loads(cookie_data)
    else:
        with open(COOKIE_FILE, "r", encoding="utf-8") as f:
            cookies = json.load(f)


    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        cookies = normalize_cookies(cookies)
        context.add_cookies(cookies)

        page = context.new_page()
        page.goto(LINKEDIN_PROFILE_URL, timeout=60000)
        page.wait_for_timeout(5000)

        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(5000)

        post_links = page.query_selector_all("a[href*='/feed/update/urn:li:']")

        new_posts = []

        for link in post_links:
            url = link.get_attribute("href")
            if not url:
                continue

            # Normalize URL
            if url.startswith("/"):
                url = "https://www.linkedin.com" + url

            # Convert feed URL to embed URL
            embed_url = url.replace(
                "https://www.linkedin.com/feed/update/",
                "https://www.linkedin.com/embed/feed/update/"
            )

            if "?collapsed=1" not in embed_url:
                embed_url += "?collapsed=1"


            if embed_url not in existing_urls:
                new_posts.append({
                    "url": embed_url,
                    "title": "LinkedIn Post",
                    "date": datetime.now().strftime("%Y-%m-%d")
                })

        if new_posts:
            print(f"✅ Found {len(new_posts)} new posts")
            save_posts(new_posts + existing_posts)
        else:
            print("ℹ️ No new posts found")

        browser.close()

if __name__ == "__main__":
    run()