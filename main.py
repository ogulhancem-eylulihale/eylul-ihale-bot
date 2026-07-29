import os
import datetime
import json
import ssl
import urllib.request
from playwright.sync_api import sync_playwright

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8982659785:AAGAChufDG5Jex36U0rtq04UavJAu9041W8")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "1386569284")

EKAP_ARAMA_KELIMELERI = [
    "Duyuru tanıtım",
    "Billboard",
    "Baskı montaj",
    "Reklam",
    "Folyo baskı",
    "Tabela",
    "Clp raket"
]

def send_telegram_message(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram token veya Chat ID bulunamadi.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }).encode("utf-8")
    
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        context = ssl._create_unverified_context()
        with urllib.request.urlopen(req, context=context) as response:
            print("Telegram bildirimi gonderildi.")
    except Exception as e:
        print(f"Telegram mesaj gonderme hatasi: {e}")

def ekap_playwright_tara():
    bulunan_ihaleler = []
    gorulen_ihale_nolari = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for kelime in EKAP_ARAMA_KELIMELERI:
            try:
                page.goto("https://ekap.kik.gov.tr/EKAP/Yayin/IhaleArama.aspx", timeout=30000)
                
                search_input = page.query_selector("input[type='text']")
                if search_input:
                    search_input.fill(kelime)
                    page.keyboard.press("Enter")
                    page.wait_for_timeout(3000)
                    
                links = page.query_selector_all("a")
                for link in links:
                    href = link.get_attribute("href") or ""
                    text = link.inner_text().strip()
                    
                    if ("IlanDetay" in href or "IhaleDetay" in href or len(text) > 15) and text not in gorulen_ihale_nolari:
                        gorulen_ihale_nolari.add(text)
                        full_link = href if href.startswith("http") else f"https://ekap.kik.gov.tr/EKAP/Yayin/{href}"
                        bulunan_ihaleler.append({
                            "kategori": kelime,
                            "baslik": text,
                            "link": full_link
                        })
            except Exception as e:
                print(f"Playwright EKAP Hata ({kelime}): {e}")

        browser.close()

    return bulunan_ihaleler

def main():
    today = datetime.date.today()
    # Önümüzdeki 30 günün zaman aralığı
    next_30_days = today + datetime.timedelta(days=30)
    
    ihaleler = ekap_playwright_tara()
    
    header = f"📋 <b>EKAP CANLI İHALE TARAMA RAPORU</b>\n"
    header += f"🗓 <b>Tarih Aralığı:</b> {today.strftime('%d.%m.%Y')} - {next_30_days.strftime('%d.%m.%Y')}\n"
    header += f"🔎 <b>Aranan Kelimeler:</b> {len(EKAP_ARAMA_KELIMELERI)} Adet\n"
    header += f"📌 <b>Bulunan İhale Sayısı:</b> {len(ihaleler)}\n"
    header += "-----------------------------------\n\n"
    
    if ihaleler:
        body = ""
        for idx, ihale in enumerate(ihaleler[:15], 1):
            body += f"{idx}. [<b>{ihale['kategori']}</b>] {ihale['baslik']}\n"
            if ihale['link']:
                body += f"🔗 <a href='{ihale['link']}'>EKAP İlan Detayı</a>\n"
            body += "\n"
    else:
        body = "EKAP üzerinde önümüzdeki 30 günlük periyotta belirttiğiniz kelimelerde aktif ilan yakalanamadı veya arama sonuçları boş döndü."
        
    send_telegram_message(header + body)

if __name__ == "__main__":
    main()
