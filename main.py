import ssl
import urllib.request
import urllib.parse
import json
import os
import xml.etree.ElementTree as ET

# SSL Sertifika Engeli Aşma
ssl._create_default_https_context = ssl._create_unverified_context

BOT_TOKEN = "8982659785:AAGAChufDG5Jex36U0rtq04UavJ"
CHAT_ID = "-1002386569284"

# FİLTRELEME KRİTERLERİ
MECRALAR = ["billboard", "bilboard", "clp", "raket", "megalight", "led", "totem", "pano", "afiş", "branda", "direk"]

SIK_OZEL_ARAMA = [
    ("duyuru", "tanıtım"),
    ("duyuru", "tanitim")
]

NET_ATISI_VARYASYONLAR = [
    ("baskı", "montaj"), ("baski", "montaj"),
    ("tabela", "montaj"), ("reklam", "montaj"),
    ("tanıtım", "materyal"), ("tanitim", "materyal"),
    ("duyuru", "pano"), ("duyuru", "panosu"),
    ("cephe", "giydirme"), ("folyo", "uygulama"),
    ("branda", "baskı"), ("dijital", "baskı")
]

def telegram_gonder(mesaj):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": CHAT_ID,
        "text": mesaj,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }).encode('utf-8')
    
    req = urllib.request.Request(
        url, 
        data=payload, 
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        urllib.request.urlopen(req)
        print("Telegram bildirimi gonderildi.")
    except Exception as e:
        print(f"Telegram Gonderim Hatasi: {e}")

def ihale_uygun_mu(metin):
    metin = metin.lower()
    
    # 1. Mecra kontrolu
    if any(m in metin for m in MECRALAR):
        return True
        
    # 2. Sık özel arama ikilileri
    for kelime1, kelime2 in SIK_OZEL_ARAMA:
        if kelime1 in metin and kelime2 in metin:
            return True
            
    # 3. Net atışı varyasyonlar
    for kelime1, kelime2 in NET_ATISI_VARYASYONLAR:
        if kelime1 in metin and kelime2 in metin:
            return True
            
    return False

def taramayi_baslat():
    # EKAP / İhale RSS Adresi
    target_url = "https://ihalehaber.com/rss" # Kendi ihale RSS/XML linkiniz
    
    try:
        req = urllib.request.Request(
            target_url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        response = urllib.request.urlopen(req)
        raw_data = response.read()
        
        # Karakter hatalarından etkilenmemek için ignore modunda decode
        xml_text = raw_data.decode('utf-8', errors='ignore')
        
        root = ET.fromstring(xml_text)
        
        # RSS veya Atom XML kontrolü
        items = root.findall('.//item') or root.findall('.//entry')
        
        bulunan = 0
        for item in items:
            title_node = item.find('title')
            link_node = item.find('link')
            desc_node = item.find('description')
            
            title = title_node.text if title_node is not None and title_node.text else ""
            link = link_node.text if link_node is not None and link_node.text else ""
            desc = desc_node.text if desc_node is not None and desc_node.text else ""
            
            # Eğer link tag'i text içermiyorsa attribute kontrol et (Atom feed'ler için)
            if not link and link_node is not None and 'href' in link_node.attrib:
                link = link_node.attrib['href']

            tam_icerik = f"{title} {desc}"
            
            if ihale_uygun_mu(tam_icerik):
                mesaj = f"📌 <b>Yeni İhale Yakalandı!</b>\n\n<b>Başlık:</b> {title}\n\n<b>Detay / Link:</b> {link}"
                telegram_gonder(mesaj)
                bulunan += 1
                
        if bulunan == 0:
            print("Tarama tamamlandi, kriterlere uygun yeni ihale bulunamadi.")
        else:
            print(f"Tarama tamamlandi. Toplam {bulunan} ihale bildirildi.")

    except Exception as e:
        print(f"Tarama Hatasi: {e}")

if __name__ == "__main__":
    taramayi_baslat()
