import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from settings import settings


def send_html_email(to: str, subject: str, html: str):
    missing = [
        name
        for name, value in {
            "EMAIL_FROM": settings.EMAIL_FROM,
            "SMTP_HOST": settings.SMTP_HOST,
            "SMTP_PORT": settings.SMTP_PORT,
            "SMTP_USER": settings.SMTP_USER,
            "SMTP_PASSWORD": settings.SMTP_PASSWORD,
        }.items()
        if not value
    ]

    if missing:
        raise RuntimeError(
            f"SMTP mal configurado. Variáveis faltando: {', '.join(missing)}"
        )

    msg = MIMEMultipart("alternative")
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to
    msg["Subject"] = subject

    msg.attach(MIMEText(html, "html", "utf-8"))

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
        server.ehlo()
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)
