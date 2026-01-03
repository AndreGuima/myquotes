from database import get_db
from fastapi import APIRouter, Depends
from schemas.auth_reset_password import ResetPasswordRequest
from services.password_reset_service import PasswordResetService
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post("/reset-password")
def reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    """
    Reseta a senha do usuário a partir de um token válido.

    ⚠️ Resposta sempre genérica para evitar enumeração de tokens.
    """

    PasswordResetService.reset_password(
        db=db,
        raw_token=data.token,
        new_password=data.new_password,
    )

    # ⚠️ Nunca revelar se o token era válido ou não
    return {"message": "Se o token for válido, a senha foi redefinida com sucesso."}
