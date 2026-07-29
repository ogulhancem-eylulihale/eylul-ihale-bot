import os
import datetime
import json
import ssl
import urllib.request
import xml.etree.ElementTree as ET

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8982659785:AAGAChufDG5Jex36U0rtq04UavJAu9041W8").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "1386569284").strip()

# Genişletilmiş Anahtar Kelime Listesi
ARAMA_KELIMELERI = [
    "duyuru", "tanıtım", "tanitim", "reklam", "baskı", "baski", "montaj", 
    "folyo", "tabela", "clp", "raket", "totem", "vinil", "billboard",
    "açıkhava", "acikhava", "mecra", "basım", "basim", "afiş", "afis",
    "branda", "led", "ekran", "direk", "pano", "branda", "matbaa", "organizasyon"
]

def send_telegram_message(message):
    token = TELEGRAM_TOKEN
    chat_id = TELEGRAM_CHAT_ID
    
    if not token or not chat_id:
        print("Telegram token veya Chat ID bulunamadi.")
        return
        
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({
        "chat_id": chat_id,
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
    return any(kw in baslik_kucuk for kw in ARAMA_KELIMELERI)

def tum_belediye_ihalelerini_tara():
    # Kaynak kategorileri artırıldı (Belediye, Hizmet, Kiralama, Mal Alımı)
    rss_urls = [
        "https://www.ilan.gov.tr/rss/kategori/belediye-ilanlari/27",
        "https://www.ilan.gov.tr/rss/kategori/ihale-ilanlari/11",
        "https://www.ilan.gov.tr/rss/kategori/hizmet-alimi/14",
        "https://www.ilan.gov.tr/rss/kategori/kiralama/19",
        "https://www.ilan.gov.tr/rss/kategori/mal-alimi/13"
    ]
    
    bulunan_ihaleler = []
    gorulen = set()
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
                    
                    if ihale_uygun_mu(title) and title not in gorulen:
                        gorulen.add(title)
                        bulunan_ihaleler.append({
                            "baslik": title,
                            "link": link
                        })
        except Exception as e:
            print(f"Tarama Hatasi ({url}): {e}")
            
    return bulunan_ihaleler

def main():
    today = datetime.date.today()
    
    ihaleler = tum_belediye_ihalelerini_tara()
    
    header = f"📋 <b>TÜM BELEDİYELER İHALE TARAMASI</b>\n"
    header += f"🗓 <b>Tarih:</b> {today.strftime('%d.%m.%Y')}\n"
    header += f"🔎 <b>Aranan Alanlar:</b> Billboard, Reklam, Açıkhava, Baskı, Tabela, CLP, Totem, Yayın vb.\n"
    header += f"📌 <b>Bulunan Sonuc Sayisi:</b> {len(ihaleler)}\n"
    header += "-----------------------------------\n\n"
    
    if ihaleler:
        body = ""
        for idx, ihale in enumerate(ihaleler[:20], 1):
            body += f"{idx}. 📌 <b>{ihale['baslik']}</b>\n"
            if ihale['link']:
                body += f"🔗 <a href='{ihale['link']}'>Ilan Detayina Git</a>\n"
            body += "\n"
    else:
        body = "Genişletilmiş arama kriterleriyle de yeni ilan bulunamadı.\nBot akışı izlemeye devam ediyor."
        
    send_telegram_message(header + body)

if __name__ == "__main__":
    main()
