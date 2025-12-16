from core.security import hash_password
from database import SessionLocal
from models.user import User


def create_default_admin():
    db = SessionLocal()

    existing_admin = db.query(User).filter(User.username == "admin").first()

    if existing_admin:
        print("⚠️ Admin já existe, pulando criação.")
        db.close()
        return

    admin = User(
        username="admin",
        email="admin@example.com",  # ✔ corrigido — email válido (antes era .local)
        password_hash=hash_password("admin123"),
        role="admin",
    )

    db.add(admin)
    db.commit()
    print("✅ Admin padrão criado.")

    db.close()
