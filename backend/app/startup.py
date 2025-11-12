from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User


def create_default_admin():
    """Cria um usuário padrão se ainda não existir."""
    db: Session = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == "admin@example.com").first()
        if not existing:
            admin_user = User(
                username="admin",
                email="admin@example.com",
                password_hash="admin123",  # Em produção, use hash seguro (ex: bcrypt)
            )
            db.add(admin_user)
            db.commit()
            print("✅ Usuário padrão criado: admin@example.com / admin123")
        else:
            print("ℹ️ Usuário padrão já existe, sem alterações.")
    finally:
        db.close()

