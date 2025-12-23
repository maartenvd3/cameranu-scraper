import requests
from bs4 import BeautifulSoup
from twilio.rest import Client
import time
import os

# ----------------------------------------------------
# INSTELLINGEN (via Render Environment Variables)
# ----------------------------------------------------
TWILIO_ACCOUNT_SID = os.getenv("USb5e1e5c486bd78677f50c00dfb986b88")
TWILIO_AUTH_TOKEN = os.getenv("7110e791ee726d085b9d39fc867775cd")

TWILIO_WHATSAPP_NUMBER = os.getenv("+14155238886")
MY_WHATSAPP_NUMBER = os.getenv("+31640439520")

# Keywords die ALLEMAAL in de titel moeten voorkomen
KEYWORDS = ["canon", "legria", "mini"]
# ----------------------------------------------------


def check_cameranu():
    """
    Check Cameranu.nl op producten waarvan de titel
    ALLE keywords bevat (slimme match).
    """
    url = "https://www.cameranu.nl/nl/c/82/camcorders"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=15)

    if response.status_code != 200:
        print("❌ Cameranu.nl niet bereikbaar")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    products = soup.find_all("a", class_="product-card__title")

    for product in products:
        name = product.get_text(strip=True)
        link = "https://www.cameranu.nl" + product.get("href")

        name_lower = name.lower()

        # Slimme keyword check
        if all(keyword in name_lower for keyword in KEYWORDS):
            print(f"✅ Match gevonden: {name}")
            return name, link

    print("ℹ️ Geen match gevonden")
    return None


def send_whatsapp_message(product_name, product_link):
    """
    Stuurt WhatsApp bericht via Twilio
    """
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    message = (
        f"📸 *Product beschikbaar!*\n\n"
        f"{product_name}\n\n"
        f"🔗 {product_link}"
    )

    client.messages.create(
        body=message,
        from_=TWILIO_WHATSAPP_NUMBER,
        to=MY_WHATSAPP_NUMBER
    )

    print("📨 WhatsApp verstuurd")


def main():
    print("🚀 Cameranu checker gestart")

    result = check_cameranu()

    if result:
        product_name, product_link = result
        send_whatsapp_message(product_name, product_link)
    else:
        print("⏳ Niets gevonden, volgende check via cron")


if __name__ == "__main__":
    main()
