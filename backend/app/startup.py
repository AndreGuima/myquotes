from app.database import SessionLocal
from app.models.user import User
from app.core.security import hash_password

def create_default_admin():
    db = SessionLocal()
    
    existing_admin = db.query(User).filter(User.username == "admin").first()

    if existing_admin:
        print("⚠️ Admin já existe, pulando criação.")
        db.close()
        return

    admin = User(
        username="admin",                     # ✔ Agora cria um usuário "admin"
        email="admin@example.com",
        password_hash=hash_password("admin123"),
        role="admin"
    )

    db.add(admin)
    db.commit()
    print("✅ Admin padrão criado.")

    db.close()
