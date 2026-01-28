from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from twilio.rest import Client
from datetime import datetime
import time

# ======================
# CONFIG
# ======================
BASE_URL = "https://www.cameranu.nl/c14732/occasions-en-demo/canon"
ZOEKWOORDEN = ["canon", "legria", "mini"]

TWILIO_SID = ""
TWILIO_AUTH_TOKEN = ""
TWILIO_WHATSAPP_FROM = ""
TWILIO_WHATSAPP_TO = ""

LOGFILE = "log.txt"
MAX_PAGES = 50

# ======================
def log(msg):
    tijd = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    regel = f"[{tijd}] {msg}"
    print(regel)  # 👈 zichtbaar in Spyder
    with open(LOGFILE, "a", encoding="utf-8") as f:
        f.write(regel + "\n")

def titel_matcht(titel):
    titel = titel.lower()
    return all(w in titel for w in ZOEKWOORDEN)

# ======================
def accepteer_cookies(driver):
    print("🔎 Controleren op cookie pop-up...")
    try:
        knop = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(., 'Alles')]")
            )
        )
        knop.click()
        print("🍪 Cookies geaccepteerd")
        time.sleep(2)
    except:
        print("ℹ️ Geen cookie pop-up gevonden")

# ======================
def haal_producten(driver):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    return soup.select("a.cat-item-product-v3__name")

# ======================
def main():
    print("🚀 Script gestart")
    log("Browser starten")

    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    try:
        driver.get(BASE_URL)
        print("🌐 Eerste pagina geladen")
        time.sleep(5)

        accepteer_cookies(driver)

        gevonden = []
        page = 1

        while page <= MAX_PAGES:
            url = BASE_URL if page == 1 else f"{BASE_URL}?page={page}"
            print(f"➡️ Bezig met pagina {page}: {url}")
            log(f"Pagina {page} openen")

            driver.get(url)
            time.sleep(4)

            producten = haal_producten(driver)
            print(f"📦 Pagina {page}: {len(producten)} producten gevonden")

            if not producten:
                print("⛔ Geen producten meer → stoppen")
                log("Geen producten meer gevonden → stoppen")
                break

            for p in producten:
                titel = p.get_text(strip=True)
                link = "https://www.cameranu.nl" + p.get("href")

                print(f"   • {titel}")
                log(f"Product: {titel}")

                if titel_matcht(titel):
                    print(f"🎯 MATCH GEVONDEN: {titel}")
                    log(f"MATCH: {titel}")
                    gevonden.append((titel, link))

            page += 1

        if not gevonden:
            print("❌ Geen Canon Legria Mini gevonden")
            log("Geen Canon Legria Mini gevonden")
            return

        print("📲 WhatsApp bericht wordt verstuurd")
        log("WhatsApp sturen")

        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

        bericht = "📷 *Canon Legria Mini gevonden op Cameranu!*\n\n"
        for titel, link in gevonden:
            bericht += f"- {titel}\n{link}\n\n"

        client.messages.create(
            from_=TWILIO_WHATSAPP_FROM,
            to=TWILIO_WHATSAPP_TO,
            body=bericht
        )

        print("✅ WhatsApp verzonden")
        log("WhatsApp verzonden")

    finally:
        driver.quit()
        print("🧹 Browser gesloten")
        log("Browser gesloten")

# ======================
if __name__ == "__main__":
    main()

