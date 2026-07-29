import os
import datetime
import json
import ssl
import urllib.request
import xml.etree.ElementTree as ET

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8982659785:AAGAChufDG5Jex36U0rtq04UavJAu9041W8").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "1386569284").strip()

# Geniş Sektörel Arama Sözlüğü
ARAMA_KELIMELERI = [
    "reklam", "baskı", "baski", "tabela", "billboard", "clp", "raket", 
    "totem", "folyo", "vinil", "montaj", "açıkhava", "acikhava", "mecra", 
    "tanıtım", "tanitim", "duyuru", "pano", "led", "direk", "afiş", "afis"
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
    return any(kw in baslik_kucuk for kw in ARAMA_KELIMELERI)

def aktif_ihaleleri_sorgula():
    # Kamu arama servislerinin ve genişletilmiş ihale kategorilerinin uç noktaları
    kategoriler = [
        "https://www.ilan.gov.tr/rss/kategori/belediye-ilanlari/27",
        "https://www.ilan.gov.tr/rss/kategori/ihale-ilanlari/11",
        "https://www.ilan.gov.tr/rss/kategori/hizmet-alimi/14",
        "https://www.ilan.gov.tr/rss/kategori/kiralama/19",
        "https://www.ilan.gov.tr/rss/kategori/mal-alimi/13"
    ]
    
    bulunan_ihaleler = []
    gorulen_basliklar = set()
    context = ssl._create_unverified_context()
    
    for url in kategoriler:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req, context=context, timeout=20) as response:
                xml_data = response.read()
                root = ET.fromstring(xml_data)
                
                for item in root.findall('.//item'):
                    title = item.find('title').text if item.find('title') is not None else ""
                    link = item.find('link').text if item.find('link') is not None else ""
                    pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""
                    
                    if ihale_uygun_mu(title) and title not in gorulen_basliklar:
                        gorulen_basliklar.add(title)
                        bulunan_ihaleler.append({
                            "baslik": title,
                            "link": link,
                            "tarih": pub_date
                        })
        except Exception as e:
            print(f"Sorgu Hatasi ({url}): {e}")
            
    return bulunan_ihaleler

def main():
    bugun = datetime.date.today().strftime('%d.%m.%Y')
    ihaleler = aktif_ihaleleri_sorgula()
    
    header = f"🚀 <b>AKTİF İHALE ARAMA RAPORU</b>\n"
    header += f"🗓 <b>Arama Tarihi:</b> {bugun} (Tarihi Gelmemiş İhaleler)\n"
    header += f"📌 <b>Bulunan Aktif İhale Sayısı:</b> {len(ihaleler)}\n"
    header += "-----------------------------------\n\n"
    
    if ihaleler:
        body = ""
        for idx, ihale in enumerate(ihaleler, 1):
            body += f"{idx}. 📌 <b>{ihale['baslik']}</b>\n"
            if ihale['link']:
                body += f"🔗 <a href='{ihale['link']}'>İhale Detayı ve İlan Metni</a>\n"
            body += "\n"
    else:
        body = "Şu an kamu yayın kaynaklarında tarihi geçmemiş eşleşen yeni ihale bulunamadı.\n\n"
        body += "💡 <b>EKAP Doğrudan Arama Bağlantıları:</b>\n"
        body += "• <a href='https://ekap.kik.gov.tr/EKAP/Oturum/IhaleArama.aspx'>EKAP Canlı İhale Arama Arayüzü</a>"
        
    send_telegram_message(header + body)

if __name__ == "__main__":
    main()
