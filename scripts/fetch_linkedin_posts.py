import os
import json
import re
from datetime import datetime
from playwright.sync_api import sync_playwright

# =======================
# CONFIGURATION
# =======================

LINKEDIN_PROFILE_URL = "https://www.linkedin.com/in/gaurav-rayat/recent-activity/all/"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_FILE = os.path.join(DATA_DIR, "linkedin_posts.json")
COOKIE_FILE = os.path.join(BASE_DIR, "linkedin_cookies.json")

# =======================
# HELPERS
# =======================

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
            "sameSite": "None"
        }
        normalized.append(cookie)
    return normalized


def load_existing_posts():
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except json.JSONDecodeError:
        # Corrupted or empty JSON → reset safely
        return []



def save_posts(posts):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)


def extract_post_urns(page):
    html = page.content()

    # This regex captures the FULL urn string
    urns = set(
        re.findall(r"urn:li:(?:activity|share):\d+", html)
    )

    return urns


# =======================
# MAIN LOGIC
# =======================

def run():
    # Load cookies (GitHub Actions OR local)
    cookie_data = os.environ.get("LINKEDIN_COOKIES")
    if cookie_data:
        raw_cookies = json.loads(cookie_data)
    else:
        if not os.path.exists(COOKIE_FILE):
            raise FileNotFoundError("linkedin_cookies.json not found")
        with open(COOKIE_FILE, "r", encoding="utf-8") as f:
            raw_cookies = json.load(f)

    cookies = normalize_cookies(raw_cookies)

    existing_posts = load_existing_posts()
    existing_urls = {p["url"] for p in existing_posts}
    seen_urls = set(existing_urls)

    new_posts = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        context.add_cookies(cookies)

        page = context.new_page()
        page.goto(LINKEDIN_PROFILE_URL, timeout=60000)

        # Wait & scroll to force post loading
        page.wait_for_timeout(5000)
        for _ in range(4):
            page.mouse.wheel(0, 4000)
            page.wait_for_timeout(3000)

        # Extract post URNs
        urns = extract_post_urns(page)

        if not urns:
            print("ℹ️ No posts detected on LinkedIn (check cookies/login)")
            browser.close()
            return

        for urn in urns:
            embed_url = f"https://www.linkedin.com/embed/feed/update/{urn}?collapsed=1"

            if embed_url in seen_urls:
                continue

            seen_urls.add(embed_url)

            new_posts.append({
                "url": embed_url,
                "title": "LinkedIn Post",
                "date": datetime.now().strftime("%Y-%m-%d")
            })

        browser.close()

    if new_posts:
        print(f"✅ Found {len(new_posts)} new posts")
        save_posts(new_posts + existing_posts)
    else:
        print("ℹ️ No new posts found")


if __name__ == "__main__":
    run()
