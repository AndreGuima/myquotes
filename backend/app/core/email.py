import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from settings import settings


def send_html_email(to: str, subject: str, html: str):
    if not settings.EMAIL_ENABLED:
        print(f"📭 EMAIL DESABILITADO (TESTING): {to} | {subject}")
        return

    if not settings.EMAIL_USER or not settings.EMAIL_PASSWORD:
        raise RuntimeError("Configurações de email não definidas")

    msg = MIMEMultipart("alternative")
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to
    msg["Subject"] = subject

    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=10) as server:
        server.starttls()
        server.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
        server.send_message(msg)

