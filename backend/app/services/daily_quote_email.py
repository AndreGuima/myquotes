from pathlib import Path

from core.email import send_html_email
from database import SessionLocal
from jinja2 import Environment, FileSystemLoader, select_autoescape
from models.user import User
from services.daily_quote_lock import acquire_daily_email_lock
from services.quote_of_the_day import get_quote_of_the_day_for_user

# --------------------------------------------------------------------
# 📨 Template engine (Jinja2)
# --------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATE_ENV = Environment(
    loader=FileSystemLoader(BASE_DIR / "templates"),
    autoescape=select_autoescape(["html", "xml"]),
)


def send_daily_quote_emails():
    db = SessionLocal()

    try:
        users = (
            db.query(User)
            .filter(User.is_active.is_(True))
            .filter(User.receive_daily_quote.is_(True))
            .all()
        )

        if not users:
            print("ℹ️ Nenhum usuário elegível para envio diário.")
            return

        template = TEMPLATE_ENV.get_template("emails/daily_quote.html")

        for user in users:
            try:
                quote = get_quote_of_the_day_for_user(db, user.id)
                if not quote:
                    continue

                html = template.render(
                    text=quote.text,
                    author=quote.author,
                    username=user.username,
                )

                send_html_email(
                    to=user.email,
                    subject="📜 Sua Quote of the Day",
                    html=html,
                )

                # 🔒 Lock diário SOMENTE após envio OK
                acquire_daily_email_lock(db, user.id)

            except Exception as e:
                print(f"❌ Erro ao enviar para {user.email}: {e}")

    finally:
        db.close()
