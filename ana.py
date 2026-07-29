import os
import datetime
import json
import ssl
import urllib.request
import xml.etree.ElementTree as ET

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8982659785:AAGAChufDG5Jex36U0rtq04UavJAu9041W8").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "1386569284").strip()

# Tam istediğin özel arama grupları
ARAMA_GRUPLARI = {
    "Duyuru & Tanıtım": ["duyuru", "tanıtım", "tanitim"],
    "Reklam & Baskı": ["reklam", "baskı", "baski"],
    "Baskı & Montaj": ["baskı", "baski", "montaj"],
    "Billboard": ["billboard"],
    "CLP & Raket": ["clp", "raket"],
    "Basılı Materyal": ["basılı materyal", "basili materyal", "matbaa", "basım", "basim"]
}

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

def baslik_grup_eslesiyor_mu(baslik, kelime_listesi):
    baslik_kucuk = baslik.lower()
    return any(kw in baslik_kucuk for kw in kelime_listesi)

def ihaleleri_tara():
    rss_urls = [
        "https://www.ilan.gov.tr/rss/kategori/belediye-ilanlari/27",
        "https://www.ilan.gov.tr/rss/kategori/ihale-ilanlari/11",
        "https://www.ilan.gov.tr/rss/kategori/hizmet-alimi/14",
        "https://www.ilan.gov.tr/rss/kategori/kiralama/19",
        "https://www.ilan.gov.tr/rss/kategori/mal-alimi/13"
    ]
    
    kategori_sonuclari = {grup: [] for grup in ARAMA_GRUPLARI.keys()}
    gorulen_basliklar = set()
    context = ssl._create_unverified_context()
    
    for url in rss_urls:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=context, timeout=15) as response:
                xml_data = response.read()
                root = ET.fromstring(xml_data)
                
                for item in root.findall('.//item'):
                    title = item.find('title').text if item.find('title') is not None else ""
                    link = item.find('link').text if item.find('link') is not None else ""
                    
                    if title in gorulen_basliklar:
                        continue
                        
                    for grup_adi, kelimeler in ARAMA_GRUPLARI.items():
                        if baslik_grup_eslesiyor_mu(title, kelimeler):
                            gorulen_basliklar.add(title)
                            kategori_sonuclari[grup_adi].append({
                                "baslik": title,
                                "link": link
                            })
                            break
        except Exception as e:
            print(f"Tarama Hatasi ({url}): {e}")
            
    return kategori_sonuclari

def main():
    bugun_str = datetime.date.today().strftime('%d.%m.%Y')
    sonuclar = ihaleleri_tara()
    
    toplam_bulunan = sum(len(v) for v in sonuclar.values())
    
    header = f"📋 <b>GÜNLÜK İHALE TARAMA RAPORU</b>\n"
    header += f"🗓 <b>Tarih:</b> {bugun_str} ve Sonrası\n"
    header += f"📌 <b>Toplam Bulunan İhale:</b> {toplam_bulunan}\n"
    header += "-----------------------------------\n\n"
    
    body = ""
    if toplam_bulunan > 0:
        for grup_adi, ihaleler in sonuclar.items():
            if ihaleler:
                body += f"🔹 <b><u>{grup_adi} Araması ({len(ihaleler)} İhale)</u></b>\n"
                for idx, ihale in enumerate(ihaleler, 1):
                    body += f"{idx}. 📌 <b>{ihale['baslik']}</b>\n"
                    if ihale['link']:
                        body += f"🔗 <a href='{ihale['link']}'>İlan Detayı</a>\n"
                body += "\n"
    else:
        body = "Bugün itibarıyla arama kelimelerinizle eşleşen tarihi geçmemiş yeni bir ihale bulunamadı.\nBot 09:30 otomatik taramalarına devam ediyor."
        
    send_telegram_message(header + body)

if __name__ == "__main__":
    main()
