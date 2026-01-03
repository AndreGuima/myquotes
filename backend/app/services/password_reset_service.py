import hashlib
import secrets
from datetime import datetime, timedelta

from models.password_reset import PasswordResetToken
from models.user import User
from sqlalchemy.orm import Session

# ==========================
# Configurações do domínio
# ==========================
TOKEN_TTL_MINUTES = 30


class PasswordResetService:
    # --------------------------------------------------
    # 🔐 Criar token de reset
    # --------------------------------------------------
    @staticmethod
    def create_reset_token(
        db: Session,
        user: User,
    ) -> str:
        """
        Cria um token de reset de senha.

        Retorna o TOKEN PURO (para envio por email).
        O banco armazena apenas o HASH.
        """

        # 1️⃣ Invalidar tokens anteriores
        db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used_at.is_(None),
        ).update(
            {"used_at": datetime.utcnow()},
            synchronize_session=False,
        )

        # 2️⃣ Gerar token seguro
        raw_token = secrets.token_urlsafe(48)

        # 3️⃣ Gerar hash do token
        token_hash = PasswordResetService._hash_token(raw_token)

        # 4️⃣ Criar registro
        reset = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=datetime.utcnow() + timedelta(minutes=TOKEN_TTL_MINUTES),
        )

        db.add(reset)
        db.commit()
        db.refresh(reset)

        # ⚠️ Retornar apenas o token puro
        return raw_token

    # --------------------------------------------------
    # 🔎 Validar token
    # --------------------------------------------------
    @staticmethod
    def validate_token(
        db: Session,
        raw_token: str,
    ) -> PasswordResetToken | None:
        """
        Valida um token de reset.

        Retorna o PasswordResetToken se válido,
        ou None se inválido / expirado / usado.
        """

        token_hash = PasswordResetService._hash_token(raw_token)

        reset = (
            db.query(PasswordResetToken)
            .filter(
                PasswordResetToken.token_hash == token_hash,
            )
            .first()
        )

        if not reset:
            return None

        if not reset.is_valid:
            return None

        return reset

    # --------------------------------------------------
    # ✅ Consumir token (após reset)
    # --------------------------------------------------
    @staticmethod
    def mark_token_as_used(
        db: Session,
        reset: PasswordResetToken,
    ) -> None:
        reset.used_at = datetime.utcnow()
        db.commit()

    # --------------------------------------------------
    # 🔒 Hash helper
    # --------------------------------------------------
    @staticmethod
    def _hash_token(raw_token: str) -> str:
        return hashlib.sha256(raw_token.encode()).hexdigest()
