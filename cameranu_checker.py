import requests
import time
import random
import os
import json
from bs4 import BeautifulSoup
from twilio.rest import Client

# =========================
# CONFIG
# =========================

BASE_URL = (
    "https://www.cameranu.nl/c14732/occasions-en-demo/canon"
    "?sort=0&show=12&t=0&f=eyJtZXJrIjpbIkNhbm9uIl19"
)

KEYWORDS = ["canon", "legria", "mini"]
STATE_FILE = "notified_products.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Connection": "keep-alive"
}

# =========================
# TWILIO CONFIG
# =========================

TWILIO_ACCOUNT_SID = os.getenv("USb5e1e5c486bd78677f50c00dfb986b88")
TWILIO_AUTH_TOKEN = os.getenv("7110e791ee726d085b9d39fc867775cd")
TWILIO_WHATSAPP_NUMBER = os.getenv("+14155238886")
MY_WHATSAPP_NUMBER = os.getenv("+31640439520")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# =========================
# STATE HANDLING
# =========================

def load_notified():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_notified(ids):
    with open(STATE_FILE, "w") as f:
        json.dump(list(ids), f)

# =========================
# WHATSAPP
# =========================

def send_whatsapp(message):
    client.messages.create(
        body=message,
        from_=TWILIO_WHATSAPP_NUMBER,
        to=MY_WHATSAPP_NUMBER
    )

# =========================
# SCRAPER
# =========================

def fetch_page(page):
    url = BASE_URL if page == 1 else f"{BASE_URL}&page={page}"
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    return response.text

def product_matches(name):
    name_lower = name.lower()
    return all(word in name_lower for word in KEYWORDS)

# =========================
# MAIN
# =========================

def main():
    print("🚀 Cameranu checker gestart")

    notified_ids = load_notified()
    found_new = False
    page = 1

    while True:
        try:
            html = fetch_page(page)
            print(f"📄 Pagina {page} opgehaald")
        except Exception as e:
            print(f"❌ Fout bij pagina {page}: {e}")
            break

        soup = BeautifulSoup(html, "html.parser")
        products = soup.select("div.cat-item-product-v3")

        if not products:
            print("ℹ️ Geen producten meer, stoppen.")
            break

        for product in products:
            product_id = product.get("data-id")
            name_tag = product.select_one("a.cat-item-product-v3__name")

            if not product_id or not name_tag:
                continue

            name = name_tag.text.strip()

            if product_matches(name):
                if product_id not in notified_ids:
                    link = "https://www.cameranu.nl" + name_tag.get("href")
                    message = (
                        "📸 *Canon Legria Mini gevonden!*\n\n"
                        f"📝 {name}\n"
                        f"🔗 {link}"
                    )
                    send_whatsapp(message)
                    notified_ids.add(product_id)
                    found_new = True
                    print(f"✅ WhatsApp verzonden voor: {name}")

        # Random delay (anti-bot)
        time.sleep(random.uniform(3, 6))
        page += 1

    save_notified(notified_ids)

    if not found_new:
        print("ℹ️ Geen nieuwe Canon Legria Mini gevonden")

if __name__ == "__main__":
    main()

