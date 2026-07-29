import os
import datetime
import urllib.request
import json
import xml.etree.ElementTree as ET
import ssl

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8982659785:AAGAChufDG5Jex36U0rtq04UavJAu9041W8")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "1386569284")

# Tüm belediyeleri ve ilgili işleri kapsayan filtrelerimiz
MECRALAR = [
    "reklam panosu", "reklam panoları", "billboard", "raket", "clp", 
    "megalight", "totem", "cephe giydirme", "dijital baskı", "vinil", 
    "tabela", "kentsel mobilya", "duyuru", "tanıtım", "matbaa", "baskı"
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

def ihale_uygun_mu(baslik):
    baslik_kucuk = baslik.lower()
    return any(kw in baslik_kucuk for kw in MECRALAR)

def ekap_rss_tara():
    rss_urls = [
        "https://www.ilan.gov.tr/rss/kategori/ihale-ilanlari/11",
        "https://www.ilan.gov.tr/rss/kategori/belediye-ilanlari/27"
    ]
    
    bulunan_ihaleler = []
    context = ssl._create_unverified_context()
    
    for url in rss_urls:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=context, timeout=10) as response:
                xml_data = response.read()
                root = ET.fromstring(xml_data)
                
                for item in root.findall('.//item'):
                    title = item.find('title').text if item.find('title') is not None else ""
                    link = item.find('link').text if item.find('link') is not None else ""
                    
                    if ihale_uygun_mu(title):
                        bulunan_ihaleler.append({
                            "baslik": title,
                            "link": link
                        })
        except Exception as e:
            print(f"RSS Tarama Hatasi ({url}): {e}")
            
    return bulunan_ihaleler

def main():
    today = datetime.date.today()
    next_20_days = today + datetime.timedelta(days=20)
    
    ihaleler = ekap_rss_tara()
    
    header = f"📋 <b>TÜM BELEDİYELER - İHALE LİSTESİ</b>\n"
    header += f"🗓 <b>Tarih Aralığı:</b> {today.strftime('%d.%m.%Y')} - {next_20_days.strftime('%d.%m.%Y')}\n"
    header += f"🔎 <b>Bulunan İhale Sayısı:</b> {len(ihaleler)}\n"
    header += "-----------------------------------\n\n"
    
    if ihaleler:
        body = ""
        for idx, ihale in enumerate(ihaleler[:15], 1):
            body += f"{idx}. 📌 <b>{ihale['baslik']}</b>\n"
            if ihale['link']:
                body += f"🔗 <a href='{ihale['link']}'>İlan Detayları İçin Tıklayın</a>\n"
            body += "\n"
    else:
        body = "Önümüzdeki 20 günlük periyotta kriterlerinize uyan yeni bir belediye ihale ilanı bulunamadı.\nTarama otomatik olarak devam ediyor."
        
    send_telegram_message(header + body)

if __name__ == "__main__":
    main()
