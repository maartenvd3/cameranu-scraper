# -*- coding: utf-8 -*-
"""
Created on Sun Dec  7 09:37:39 2025

@author: mcjvd
"""

import requests
from bs4 import BeautifulSoup
from twilio.rest import Client
import time

# ----------------------------------------------------
# VUL DIT IN (JOUW GEGEVENS)
# ----------------------------------------------------
TWILIO_ACCOUNT_SID = "USb5e1e5c486bd78677f50c00dfb986b88"
TWILIO_AUTH_TOKEN = "7110e791ee726d085b9d39fc867775cd"

TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"    # Twilio Sandbox nummer
MY_WHATSAPP_NUMBER = "whatsapp:+31640439520"         # Jouw eigen nummer

# Het model dat je wil zoeken op Cameranu.nl
TARGET_MODEL = "Canon Legria Mini"
# -----------------------------------------------------


def check_cameranu():
    url = "https://www.cameranu.nl/nl/c/82/camcorders"
    response = requests.get(url)

    if response.status_code != 200:
        print("Kon de website niet bereiken.")
        return False

    soup = BeautifulSoup(response.text, "html.parser")
    products = soup.find_all("a", class_="product-card__title")

    for product in products:
        name = product.get_text(strip=True)
        link = "https://www.cameranu.nl" + product.get("href")

        if TARGET_MODEL.lower() in name.lower():
            return link

    return None


def send_whatsapp_message(message):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(
        body=message,
        from_=TWILIO_WHATSAPP_NUMBER,
        to=MY_WHATSAPP_NUMBER
    )


def main():
    print("AI scraper gestart... Checking ieder uur.\n")

    while True:
        result = check_cameranu()
        if result:
            msg = f"📸 Goed nieuws! De *{TARGET_MODEL}* is beschikbaar!\n\nLink: {result}"
            send_whatsapp_message(msg)
            print("Model gevonden! WhatsApp verstuurd.")
        else:
            print(f"{TARGET_MODEL} niet gevonden. Nieuwe check over 1 uur...")

        time.sleep(3600)


if __name__ == "__main__":
    main()
