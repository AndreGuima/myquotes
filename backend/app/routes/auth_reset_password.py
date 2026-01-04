import logging
from datetime import UTC, datetime

from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from models.password_reset import PasswordResetToken
from schemas.auth_reset_password import ResetPasswordRequest
from services.password_reset_service import PasswordResetService
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.get("/reset-password/validate")
def validate_reset_token(
    token: str,
    db: Session = Depends(get_db),
):
    token_hash = PasswordResetService._hash_token(token)

    reset = (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.used_at.is_(None),
            PasswordResetToken.expires_at > datetime.now(UTC),
        )
        .first()
    )

    if not reset:
        raise HTTPException(status_code=410, detail="Token inválido ou expirado")

    return {"valid": True}


@router.post("/reset-password")
def reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    """
    Reseta a senha do usuário a partir de um token válido.

    ⚠️ Resposta sempre genérica para evitar enumeração de tokens.
    """

    success = PasswordResetService.reset_password(
        db=db,
        raw_token=data.token,
        new_password=data.new_password,
    )

    if not success:
        logger.warning("Invalid password reset attempt")

    return {"message": "Se o token for válido, a senha foi redefinida com sucesso."}
