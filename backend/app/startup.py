import logging

from core.security import hash_password
from database import SessionLocal
from models.user import User

# ============================================================
# 🧠 Logger de startup
# ============================================================

logger = logging.getLogger("app.startup")


def create_default_admin():
    db = SessionLocal()

    try:
        existing_admin = db.query(User).filter(User.username == "admin").first()

        if existing_admin:
            logger.warning("Admin padrão já existe, pulando criação")
            return

        admin = User(
            username="admin",
            email="admin@example.com",
            password_hash=hash_password("admin123"),
            role="admin",
        )

        db.add(admin)
        db.commit()

        logger.info("Admin padrão criado com sucesso")

    except Exception:
        db.rollback()
        logger.exception("Erro ao criar admin padrão")

    finally:
        db.close()
