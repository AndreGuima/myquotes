from core.security import verify_password
from models.user import User
from services.password_reset_service import PasswordResetService


def test_reset_password_rejects_weak_password(db_sessionmaker, client):
    db = db_sessionmaker()
    try:
        user = User(
            email="reset@test.com",
            username="reset",
            password_hash="oldhash",
            is_active=True,
            is_verified=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        token = PasswordResetService.create_reset_token(db, user)

        r = client.post(
            "/auth/reset-password",
            json={
                "token": token,
                "new_password": "12345678",  # fraca
            },
        )

        assert r.status_code == 422

        db.refresh(user)
        assert user.password_hash == "oldhash"

    finally:
        db.close()
