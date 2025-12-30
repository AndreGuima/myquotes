from datetime import datetime, time
from pathlib import Path

from core.email import send_html_email
from database import SessionLocal
from jinja2 import Environment, FileSystemLoader, select_autoescape
from models.user import User
from services.daily_quote_lock import try_acquire_daily_email_lock
from services.quote_of_the_day import get_quote_of_the_day_for_user
from services.user_preferences_service import get_user_preferences
from sqlalchemy.orm import Session

# ============================================================
# 📁 Templates
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATE_ENV = Environment(
    loader=FileSystemLoader(BASE_DIR / "templates"),
    autoescape=select_autoescape(["html", "xml"]),
)

# ============================================================
# ⚙️ Defaults
# ============================================================

PREFERENCE_CATEGORY = "quotes"
DEFAULT_QUOTE_TIME = time(8, 0)

# ============================================================
# 📧 Job principal
# ============================================================


def send_daily_quote_emails():
    db: Session = SessionLocal()

    try:
        users = (
            db.query(User)
            .filter(
                User.is_active.is_(True),
                User.is_verified.is_(True),
            )
            .all()
        )

        template = TEMPLATE_ENV.get_template("emails/daily_quote.html")
        now = datetime.now()

        print(f"⏰ Cron iniciado em {now.isoformat()} (UTC)")
        print(f"👥 Usuários ativos: {len(users)}")

        for user in users:
            try:
                _process_user(
                    db=db,
                    user=user,
                    now=now,
                    template=template,
                )
            except Exception as e:
                db.rollback()
                print(f"❌ Erro ao processar {user.email}: {e}")

        print("🏁 Execução do cron finalizada")

    finally:
        db.close()


# ============================================================
# 🔁 Processamento por usuário
# ============================================================


def _process_user(
    db: Session,
    user: User,
    now: datetime,
    template,
):
    # 🔔 Preferências (JSON)
    prefs = get_user_preferences(db, user.id, PREFERENCE_CATEGORY)

    if not prefs.get("receive_daily_quote", True):
        print(f"🔕 {user.email} desativou quote diária")
        return

    # ⏰ Horário
    time_str = prefs.get("daily_quote_time")
    if time_str:
        hour, minute = map(int, time_str.split(":"))
        user_time = time(hour, minute)
    else:
        user_time = DEFAULT_QUOTE_TIME

    scheduled = datetime.combine(now.date(), user_time)

    if now < scheduled:
        print(f"⏭️ {user.email} — agora={now.time()} agendado={user_time}")
        return

    # 🔒 Lock diário
    lock = try_acquire_daily_email_lock(db, user.id)
    if not lock:
        print(f"🔒 Lock já existe para {user.email}, pulando envio")
        return

    # 📜 Quote do dia
    quote = get_quote_of_the_day_for_user(db, user.id)
    if not quote:
        print(f"⚠️ Nenhuma quote encontrada para {user.email}")
        db.rollback()
        return

    html = template.render(
        text=quote.text,
        author=quote.author,
        username=user.username,
    )

    # 📨 Envio
    send_html_email(
        to=user.email,
        subject="📜 Quote of the Day",
        html=html,
    )

    db.commit()
    print(f"✅ Email enviado para {user.email}")
