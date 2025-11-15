from app.database import SessionLocal
from app.models.user import User
from app.core.security import hash_password


def create_default_admin():
    db = SessionLocal()
    admin = db.query(User).filter_by(username="admin").first()

    if not admin:
        admin = User(
            username="admin",
            email="andrepaivaguimaraes@gmail.com",
            password_hash=hash_password("admin"),
            role="admin"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

    db.close()
