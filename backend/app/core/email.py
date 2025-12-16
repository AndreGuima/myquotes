import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from settings import settings


def send_html_email(to: str, subject: str, html: str):
    if not settings.EMAIL_ENABLED:
        print(f"📭 EMAIL DESABILITADO: {to} | {subject}")
        return

    msg = MIMEMultipart("alternative")
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to
    msg["Subject"] = subject

    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP(
        settings.SMTP_HOST,
        settings.SMTP_PORT,
        timeout=10,
    ) as server:

        # 🔐 LOGIN apenas se existir (MailHog não precisa)
        if settings.SMTP_USER and settings.SMTP_PASSWORD:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

        server.send_message(msg)
