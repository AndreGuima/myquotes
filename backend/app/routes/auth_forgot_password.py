from database import get_db
from fastapi import APIRouter, Depends
from models.user import User
from schemas.auth_forgot_password import ForgotPasswordRequest
from services.email_service import EmailService
from services.password_reset_service import PasswordResetService
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post("/forgot-password")
def forgot_password(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    """
    Solicita reset de senha.

    ⚠️ Sempre retorna sucesso para evitar enumeração de usuários.
    """

    user = db.query(User).filter(User.email == data.email).first()

    if user:
        token = PasswordResetService.create_reset_token(db, user)
        EmailService.send_password_reset_email(
            email=user.email,
            reset_token=token,
        )

    return {
        "message": "Se o email existir, enviaremos instruções para redefinir a senha."
    }
