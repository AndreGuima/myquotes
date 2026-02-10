from datetime import UTC, datetime, timedelta

from core.security import hash_password, verify_password
from models.password_reset import PasswordResetToken
from models.user import User
from services.password_reset_service import PasswordResetService
from sqlalchemy.orm import Session


# ============================================================
# Helpers
# ============================================================
def create_user(
    db: Session,
    email=None,
    username="user_test",
    password="oldpassword",
):
    if email is None:
        email = f"user_{datetime.now(UTC).timestamp()}@test.com"

    user = User(
        email=email,
        username=username,
        password_hash=hash_password(password),
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_valid_token(db: Session, user: User) -> str:
    return PasswordResetService.create_reset_token(db, user)


# ============================================================
# Tests
# ============================================================


def test_reset_password_success(client, db_sessionmaker):
    db = db_sessionmaker()

    try:

        user = create_user(db)
        token = create_valid_token(db, user)

        response = client.post(
            "/auth/reset-password",
            json={
                "token": token,
                "new_password": "Newpassword123!",
            },
        )

        assert response.status_code == 200

        # senha foi alterada
        db.refresh(user)
        assert verify_password("Newpassword123!", user.password_hash)

    finally:
        db.close()


def test_reset_password_invalid_token(client, db_sessionmaker):
    db = db_sessionmaker()

    try:
        user = create_user(db)

        response = client.post(
            "/auth/reset-password",
            json={
                "token": "invalid-token",
                "new_password": "newpassword123",
            },
        )

        assert response.status_code == 200

        db.refresh(user)
        assert verify_password("oldpassword", user.password_hash)

    finally:
        db.close()


def test_reset_password_expired_token(client, db_sessionmaker):
    db = db_sessionmaker()

    try:
        user = create_user(db)

        raw_token = "expired-token"
        token_hash = PasswordResetService._hash_token(raw_token)

        expired = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=datetime.now(UTC) - timedelta(minutes=1),
        )

        db.add(expired)
        db.commit()

        response = client.post(
            "/auth/reset-password",
            json={
                "token": raw_token,
                "new_password": "newpassword123",
            },
        )

        assert response.status_code == 200

        db.refresh(user)
        assert verify_password("oldpassword", user.password_hash)

    finally:
        db.close()


def test_reset_password_token_reuse_fails(client, db_sessionmaker):
    db = db_sessionmaker()

    try:

        user = create_user(db)
        token = create_valid_token(db, user)

        # primeira tentativa
        r1 = client.post(
            "/auth/reset-password",
            json={
                "token": token,
                "new_password": "Newpassword123!",
            },
        )

        assert r1.status_code == 200
        db.refresh(user)
        assert verify_password("Newpassword123!", user.password_hash)

        # segunda tentativa com o MESMO token
        r2 = client.post(
            "/auth/reset-password",
            json={
                "token": token,
                "new_password": "Anotherpassword123!",
            },
        )

        assert r2.status_code == 200
        db.refresh(user)

        # senha não muda novamente
        assert not verify_password("Anotherpassword123!", user.password_hash)

    finally:
        db.close()


def test_reset_password_invalidates_all_tokens(client, db_sessionmaker):
    db = db_sessionmaker()
    try:
        user = create_user(db)

        token1 = create_valid_token(db, user)  # token antigo, deve ser invalidado

        # criar token2 invalida token1
        token2 = create_valid_token(db, user)

        # usar token2 (o ÚNICO válido)
        client.post(
            "/auth/reset-password",
            json={
                "token": token2,
                "new_password": "Newpassword123!",
            },
        )

        db.refresh(user)
        assert verify_password("Newpassword123!", user.password_hash)

        # token2 deve estar invalidado
        r = client.post(
            "/auth/reset-password",
            json={
                "token": token2,
                "new_password": "anotherpassword",
            },
        )

        assert r.status_code == 200
        db.refresh(user)
        assert not verify_password("anotherpassword", user.password_hash)

    finally:
        db.close()


def test_validate_reset_token_success(client, db_sessionmaker):
    db = db_sessionmaker()
    try:
        user = create_user(db)
        token = create_valid_token(db, user)

        r = client.get(
            "/auth/reset-password/validate",
            params={"token": token},
        )

        assert r.status_code == 200
        assert r.json() == {"valid": True}

    finally:
        db.close()


def test_validate_reset_token_invalid(client):
    r = client.get(
        "/auth/reset-password/validate",
        params={"token": "invalid"},
    )

    assert r.status_code == 410  # Gone
