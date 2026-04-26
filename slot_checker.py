import os
import requests

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
URL = os.getenv("TARGET_URL")

def notify(msg):
    requests.get(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        params={"chat_id": CHAT_ID, "text": msg}
    )

try:
    r = requests.get(URL, timeout=10)
    html = r.text.lower()

    # Debug: log page content and status
    print(f"Status code: {r.status_code}")
    print(f"Response length: {len(html)} characters")
    print(f"HTML content:\n{html[:2000]}")  # First 2000 chars for debugging

    if "aucun créneau" not in html:
        notify(f"RDV AVAILABLE!\n\n{URL}")
        exit(1)

    print("No slots found")

except Exception as e:
    notify(f"ERROR: {e}")
    exit(1)