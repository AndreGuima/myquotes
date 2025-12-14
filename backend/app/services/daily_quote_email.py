from pathlib import Path

from core.email import send_html_email
from database import SessionLocal
from jinja2 import Environment, FileSystemLoader, select_autoescape
from models.user import User
from services.quote_of_the_day import get_quote_of_the_day_for_user

# --------------------------------------------------------------------
# 📨 Template engine (Jinja2)
# --------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[2]

TEMPLATE_ENV = Environment(
    loader=FileSystemLoader(BASE_DIR / "templates"),
    autoescape=select_autoescape(["html", "xml"]),
)


def send_daily_quote_emails():
    """
    Envia a Quote of the Day por email para todos os usuários
    ativos e opt-in.
    """

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

                html = template.render(
                    text=quote.text,
                    author=quote.author,
                    username=user.username,
                )

                send_html_email(
                    to=user.email,
                    subject="📜 Quote of the Day",
                    html=html,
                )

            except Exception as e:
                # ⚠️ Um erro não deve parar o envio inteiro
                print(f"❌ Erro ao enviar para {user.email}: {e}")

    finally:
        db.close()
