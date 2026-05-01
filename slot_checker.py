import os
import requests
import smtplib
from email.message import EmailMessage

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
URL = os.getenv("TARGET_URL")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
EMAIL_RECIPIENTS = os.getenv("EMAIL_RECIPIENTS", "")


def load_recipients():
    # Comma-separated list, e.g. "a@example.com,b@example.com"
    recipients = [email.strip() for email in EMAIL_RECIPIENTS.split(",") if email.strip()]

    # Deduplicate while preserving input order.
    return list(dict.fromkeys(recipients))


def notify_telegram(msg):
    if not TOKEN or not CHAT_ID:
        return

    requests.get(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        params={"chat_id": CHAT_ID, "text": msg},
        timeout=10,
    )


def notify_email(msg):
    recipients = load_recipients()

    if not recipients:
        print("Email notifications skipped: no recipients configured")
        return

    if not EMAIL_SENDER or not EMAIL_APP_PASSWORD:
        print("Email notifications skipped: EMAIL_SENDER or EMAIL_APP_PASSWORD is missing")
        return

    email_message = EmailMessage()
    email_message["Subject"] = "Slot Checker Alert"
    email_message["From"] = EMAIL_SENDER
    email_message["To"] = ", ".join(recipients)
    email_message.set_content(msg)

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.login(EMAIL_SENDER, EMAIL_APP_PASSWORD)
        smtp.send_message(email_message)

def notify(msg):
    notify_telegram(msg)
    notify_email(msg)

try:
    r = requests.get(URL, timeout=10)
    html = r.text.lower()

    # Debug: log page content and status
    print(f"Status code: {r.status_code}")
    print(f"Response length: {len(html)} characters")
    print(f"HTML content:\n{html}")

    if "aucun créneau" not in html:
        notify(f"RDV Disponible!\n\n{URL}")
        exit(1)

    print("No slots found")

except Exception as e:
    notify(f"ERROR: {e}")
    exit(1)