import os
import datetime
import urllib.request
import json

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8982659785:AAGAChufDG5Jex36U0rtq04UavJAu9041W8")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "1386569284")

def send_telegram_message(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram token veya Chat ID bulunamadi.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }).encode("utf-8")
    
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as response:
            print("Telegram bildirimi gonderildi.")
    except Exception as e:
        print(f"Telegram mesaj gonderme hatasi: {e}")

def main():
    today = datetime.date.today()
    next_20_days = today + datetime.timedelta(days=20)
    
    header = f"📋 <b>EKAP / İhale Özet Raporu</b>\n"
    header += f"🗓 <b>Tarih Aralığı:</b> {today.strftime('%d.%m.%Y')} - {next_20_days.strftime('%d.%m.%Y')}\n"
    header += "-----------------------------------\n"
    
    body = "Önümüzdeki 20 gün için aktif ihaleler taranıyor.\n"
    body += "Bot sorunsuz çalışıyor ve zamanlayıcı aktif!"
    
    send_telegram_message(header + body)

if __name__ == "__main__":
    main()
