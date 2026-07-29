import os
import datetime
import urllib.request
import urllib.parse
import json
import ssl
from bs4 import BeautifulSoup

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8982659785:AAGAChufDG5Jex36U0rtq04UavJAu9041W8")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "1386569284")

# EKAP'ta elle aradığın 7 temel anahtar kelime
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

def ekap_tara():
    bulunan_ihaleler = []
    gorulen_ihale_nolari = set()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    context = ssl._create_unverified_context()

    for kelime in EKAP_ARAMA_KELIMELERI:
        try:
            # EKAP Arama URL yapısı
            encoded_query = urllib.parse.quote(kelime)
            search_url = f"https://ekap.kik.gov.tr/EKAP/Yayin/IhaleArama.aspx?k={encoded_query}"
            
            req = urllib.request.Request(search_url, headers=headers)
            with urllib.request.urlopen(req, context=context, timeout=15) as response:
                html_content = response.read().decode('utf-8', errors='ignore')
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # EKAP sonuç tablolarını / kartlarını tarama
                # EKAP ilan satırlarını veya linklerini yakalama
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    text = link.get_text(strip=True)
                    
                    if "IlanDetay" in href or "IhaleDetay" in href or len(text) > 20:
                        full_link = href if href.startswith("http") else f"https://ekap.kik.gov.tr/EKAP/Yayin/{href}"
                        
                        if full_link not in gorulen_ihale_nolari and len(text) > 10:
                            gorulen_ihale_nolari.add(full_link)
                            bulunan_ihaleler.append({
                                "kategori": kelime,
                                "baslik": text,
                                "link": full_link
                            })
        except Exception as e:
            print(f"EKAP Tarama Hatasi ({kelime}): {e}")
            
    return bulunan_ihaleler

def main():
    today = datetime.date.today()
    next_20_days = today + datetime.timedelta(days=20)
    
    ihaleler = ekap_tara()
    
    header = f"📋 <b>EKAP İHALE TARAMA RAPORU</b>\n"
    header += f"🗓 <b>Tarih Aralığı:</b> {today.strftime('%d.%m.%Y')} - {next_20_days.strftime('%d.%m.%Y')}\n"
    header += f"🔎 <b>Aranan Kelimeler:</b> {len(EKAP_ARAMA_KELIMELERI)} Adet\n"
    header += f"📌 <b>Bulunan Toplam Sonuç:</b> {len(ihaleler)}\n"
    header += "-----------------------------------\n\n"
    
    if ihaleler:
        body = ""
        for idx, ihale in enumerate(ihaleler[:15], 1):
            body += f"{idx}. [<b>{ihale['kategori']}</b>] {ihale['baslik']}\n"
            body += f"🔗 <a href='{ihale['link']}'>EKAP İlanına Git</a>\n\n"
    else:
        body = "EKAP üzerinde belirlediğiniz 7 anahtar kelimede şu an aktif ilan yakalanamadı veya EKAP güvenlik duvarı isteği engelledi.\nTarama otomatik periyotta tekrarlanacak."
        
    send_telegram_message(header + body)

if __name__ == "__main__":
    main()
