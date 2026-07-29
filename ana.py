import os
import datetime
import json
import urllib.request

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8982659785:AAGAChufDG5Jex36U0rtq04UavJAu9041W8").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "1386569284").strip()

def send_telegram_message(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram bilgileri eksik.")
        return
        
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }).encode("utf-8")
    
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as response:
            print("Telegram bildirimi başarıyla gönderildi.")
    except Exception as e:
        print(f"Mesaj gönderme hatası: {e}")

def main():
    today_str = datetime.date.today().strftime('%d.%m.%Y')
    
    # EKAP Doğrudan Arama ve İlan.gov.tr Filtreli Bağlantıları
    ekap_adana_link = "https://ekap.kik.gov.tr/EKAP/Oturum/IhaleArama.aspx"
    ilan_gov_reklam = "https://www.ilan.gov.tr/arama?q=reklam"
    ilan_gov_baski = "https://www.ilan.gov.tr/arama?q=bask%C4%B1"
    ilan_gov_billboard = "https://www.ilan.gov.tr/arama?q=billboard"
    ilan_gov_tabela = "https://www.ilan.gov.tr/arama?q=tabela"

    msg = f"🎯 <b>GÜNLÜK AKTİF İHALE CANLI TAKİP PANELİ</b>\n"
    msg += f"🗓 <b>Tarih:</b> {today_str} (30 Temmuz ve Sonrası İhaleler)\n"
    msg += "-----------------------------------\n\n"
    
    msg += "🏛 <b>1. EKAP (Tüm Türkiye & Kamu İhaleleri)</b>\n"
    msg += "EKAP üzerindeki tarihi geçmemiş tüm aktif ihaleleri canlı sorgulamak için aşağıdaki bağlantıyı kullanın:\n"
    msg += f"🔗 <a href='{ekap_adana_link}'>EKAP Canlı İhale Arama Ekranına Git</a>\n\n"
    
    msg += "📢 <b>2. İLAN.GOV.TR (Doğrudan Kategori Aramaları)</b>\n"
    msg += f"• 🔹 <a href='{ilan_gov_reklam}'>Aktif Reklam ve Yayın İhaleleri</a>\n"
    msg += f"• 🔹 <a href='{ilan_gov_baski}'>Aktif Baskı, Matbaa ve Dijital İhaleleri</a>\n"
    msg += f"• 🔹 <a href='{ilan_gov_billboard}'>Aktif Billboard, CLP, Raket ve Mecra İhaleleri</a>\n"
    msg += f"• 🔹 <a href='{ilan_gov_tabela}'>Aktif Tabela, Totem ve Montaj İhaleleri</a>\n\n"
    
    msg += "-----------------------------------\n"
    msg += "⚡ <i>Bot her gün bu filtreleri güncelleyerek bildirim göndermeye devam edecektir.</i>"

    send_telegram_message(msg)

if __name__ == "__main__":
    main()
