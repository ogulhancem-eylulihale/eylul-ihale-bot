import os
import datetime
import json
import urllib.request
import ssl

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8982659785:AAGAChufDG5Jex36U0rtq04UavJAu9041W8").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "1386569284").strip()

# Aranacak Sektörel Kelimeler
KELIMELER = [
    "reklam", "baskı", "baski", "tabela", "billboard", "clp", "raket", 
    "totem", "folyo", "vinil", "montaj", "açıkhava", "acikhava", "mecra", 
    "tanıtım", "tanitim", "duyuru", "pano", "led", "afiş", "afis"
]

def send_telegram_message(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram bilgileri eksik.")
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
        print(f"Mesaj gonderme hatasi: {e}")

def ekap_api_sorgula():
    # EKAP'in arka planda calisan kamuya acik arama servisi
    url = "https://ekapv2.kik.gov.tr/api/IhaleArama/Arama"
    
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    # EKAP'a gonderilen dogrudan sorgu paketi
    payload = json.dumps({
        "IhaleTarihiBaslangic": today,
        "SayfaBoyutu": 100,
        "SayfaNo": 1,
        "SiralamaKriteri": "IhaleTarihi",
        "SiralamaYonu": "ASC"
    }).encode("utf-8")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*"
    }
    
    bulunanlar = []
    
    try:
        context = ssl._create_unverified_context()
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, context=context, timeout=20) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            
            # EKAP'tan donen ihale listesini süzüyoruz
            ihaleler = res_data.get("data", {}).get("items", []) if isinstance(res_data.get("data"), dict) else []
            
            for ihale in ihaleler:
                is_adi = ihale.get("isAdi", "") or ihale.get("ihaleAdi", "")
                ihale_no = ihale.get("ihaleKayitNo", "")
                idare_adi = ihale.get("idareAdi", "")
                tarih = ihale.get("ihaleTarihi", "")
                
                # Sektorel kelime kontrolu
                if any(kw in is_adi.lower() for kw in KELIMELER):
                    bulunanlar.append({
                        "baslik": is_adi,
                        "no": ihale_no,
                        "idare": idare_adi,
                        "tarih": tarih
                    })
    except Exception as e:
        print(f"EKAP API Bağlantı Hatası: {e}")
        
    return bulunanlar

def main():
    bugun_str = datetime.date.today().strftime('%d.%m.%Y')
    
    # EKAP Doğrudan Taraması
    ihaleler = ekap_api_sorgula()
    
    header = f"🚨 <b>EKAP GELECEK İHALELER BİLDİRİMİ</b>\n"
    header += f"🗓 <b>Arama Tarihi:</b> {bugun_str} ve Sonrası\n"
    header += f"📌 <b>Yakalanan İhale Sayısı:</b> {len(ihaleler)}\n"
    header += "-----------------------------------\n\n"
    
    if ihaleler:
        body = ""
        for idx, ihale in enumerate(ihaleler, 1):
            body += f"<b>{idx}. {ihale['baslik']}</b>\n"
            body += f"🏢 <b>İdare:</b> {ihale['idare']}\n"
            body += f"🔢 <b>İKN:</b> {ihale['no']}\n"
            if ihale['tarih']:
                body += f"📅 <b>İhale Tarihi:</b> {ihale['tarih']}\n"
            body += "-----------------------------------\n"
    else:
        body = "EKAP veritabanında bugünden itibaren yayınlanmış yeni bir reklam/baskı ihaleli eşleşmesi bulunamadı.\nBot arka planda kontrol etmeye devam ediyor."
        
    send_telegram_message(header + body)

if __name__ == "__main__":
    main()
