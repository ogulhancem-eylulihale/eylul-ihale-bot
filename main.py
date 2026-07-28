import urllib.request
import json
import xml.etree.ElementTree as ET
import time

BOT_TOKEN = "8982659785:AAGAChufDG5Jex36U0rtq04UavJAu9041W8"
CHAT_ID = "1386569284"

OZEL_MECRALAR = ["billboard", "bilboard", "clp", "raket", "totem", "megalight"]

BIRLESIK_OZEL_ARAMA = [
    ("duyuru", "tanıtım"),
    ("duyuru", "tanitim")
]

NOKTA_ATISI_VARYASYONLAR = [
    ("baskı", "montaj"), ("baski", "montaj"),
    ("tabela", "montaj"), ("reklam", "montaj"),
    ("tanıtım", "materyal"), ("tanitim", "materyal"),
    ("duyuru", "pano"), ("duyuru", "panosu"),
    ("cephe", "giydirme"), ("folyo", "uygulama"),
    ("branda", "baskı"), ("dijital", "baskı"),
    ("ışıklı", "tabela"), ("isikli", "tabela")
]

HARIC_KELIMELER = ["asfalt", "betonarme", "bina yapımı", "kanalizasyon", "hafriyat", "kilit taşı"]

def telegram_mesaj_gonder(mesaj):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": CHAT_ID, 
        "text": mesaj, 
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    try:
        urllib.request.urlopen(req)
    except Exception as e:
        print("Telegram Hata:", e)

def ihale_tara_ve_bildir():
    rss_url = "https://www.ilan.gov.tr/rss/kategori/ihale"
    req = urllib.request.Request(rss_url, headers={'User-Agent': 'Mozilla/5.0'})
    
    try:
        response = urllib.request.urlopen(req)
        xml_data = response.read()
        root = ET.fromstring(xml_data)
        
        bulunan_sayisi = 0
        gonderilen_linkler = set()

        for item in root.findall('./channel/item'):
            baslik = item.find('title').text if item.find('title') is not None else ""
            link = item.find('link').text if item.find('link') is not None else ""
            pubDate = item.find('pubDate').text if item.find('pubDate') is not None else ""
            baslik_lower = baslik.lower()
            
            if link in gonderilen_linkler:
                continue

            if any(haric in baslik_lower for haric in HARIC_KELIMELER):
                continue
                
            eslesme_sebebi = None

            for k1, k2 in BIRLESIK_OZEL_ARAMA:
                if k1 in baslik_lower and k2 in baslik_lower:
                    eslesme_sebebi = f"Özel Birleşik Arama: '{k1.capitalize()} {k2.capitalize()}'"
                    break

            if not eslesme_sebebi:
                for mecra in OZEL_MECRALAR:
                    if mecra in baslik_lower:
                        eslesme_sebebi = f"Özel Mecra: '{mecra.upper()}'"
                        break

            if not eslesme_sebebi:
                for k1, k2 in NOKTA_ATISI_VARYASYONLAR:
                    if k1 in baslik_lower and k2 in baslik_lower:
                        eslesme_sebebi = f"Nokta Atışı Varyasyon: '{k1} + {k2}'"
                        break

            if eslesme_sebebi:
                bulunan_sayisi += 1
                gonderilen_linkler.add(link)
                
                mesaj = (
                    f"🎯 <b>Adana & Hedef İhale Yakalandı!</b>\n\n"
                    f"🔎 <b>Yakalama Sebebi:</b> {eslesme_sebebi}\n"
                    f"📌 <b>İlan Başlığı:</b>\n{baslik}\n"
                    f"📅 <b>Yayın Tarihi:</b> {pubDate[:16]}\n\n"
                    f"🔗 <a href='{link}'>İhaleyi İncele / Şartnameye Git</a>"
                )
                telegram_mesaj_gonder(mesaj)
                time.sleep(1.5)
                
        if bulunan_sayisi == 0:
            telegram_mesaj_gonder("ℹ️ <b>Otomatik Tarama:</b> Yeni bir hedef ihale bulunamadı.")
            
    except Exception as e:
        print("Tarama Hatası:", e)

ihale_tara_ve_bildir()
