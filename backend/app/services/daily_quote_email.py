from datetime import datetime, time
from pathlib import Path

from core.email import send_html_email
from database import SessionLocal
from jinja2 import Environment, FileSystemLoader, select_autoescape
from models.user import User
from services.daily_quote_lock import try_acquire_daily_email_lock
from services.quote_of_the_day import get_quote_of_the_day_for_user

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

        template = TEMPLATE_ENV.get_template("emails/daily_quote.html")
        now = datetime.now()

        print(f"⏰ Cron iniciado em {now.isoformat()} (UTC)")
        print(f"👥 Usuários elegíveis: {len(users)}")

        for user in users:
            try:
                # ⏰ horário do usuário
                user_time = user.daily_quote_time or time(8, 0)
                scheduled = datetime.combine(now.date(), user_time)

                # ✅ regra sem perda
                if now < scheduled:
                    print(f"⏭️ {user.email} — agora={now.time()} agendado={user_time}")
                    continue

                # 🔒 tenta adquirir lock (SEM commit)
                lock = try_acquire_daily_email_lock(db, user.id)
                if not lock:
                    print(f"🔒 Lock já existe para {user.email}, pulando envio")
                    continue

                # 📜 quote do dia
                quote = get_quote_of_the_day_for_user(db, user.id)
                if not quote:
                    print(f"⚠️ Nenhuma quote encontrada para {user.email}")
                    db.rollback()
                    continue

                html = template.render(
                    text=quote.text,
                    author=quote.author,
                    username=user.username,
                )

                # 📨 envio
                send_html_email(
                    to=user.email,
                    subject="📜 Quote of the Day",
                    html=html,
                )

                # ✅ somente agora confirma tudo
                db.commit()
                print(f"✅ Email enviado para {user.email}")

            except Exception as e:
                db.rollback()
                print(f"❌ Erro ao processar {user.email}: {e}")

        print("🏁 Execução do cron finalizada")

    finally:
        db.close()
