from datetime import UTC, datetime, timedelta

from jose import jwt
from passlib.context import CryptContext

# ============================================================
# 🔧 Configurações de segurança
# ============================================================

SECRET_KEY = "MYQUOTES_SUPER_SECRET_KEY_123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============================================================
# 🔐 HASH / VERIFICAÇÃO DE SENHA
# ============================================================


def hash_password(password: str) -> str:
    """Gera hash seguro para armazenar no banco."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compara senha enviada com hash salvo."""
    return pwd_context.verify(plain_password, hashed_password)


# ============================================================
# 🔐 JWT - CRIAÇÃO E VALIDAÇÃO DE TOKENS
# ============================================================


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Cria um token JWT assinado (para login)."""
    to_encode = data.copy()

    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str):
    """Valida e decodifica um token JWT."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        return None


def create_email_verification_token(user_id: int):
    """Cria um token JWT para verificação de email (válido por 24h)."""
    expire = datetime.now(UTC) + timedelta(hours=24)

    payload = {
        "sub": str(user_id),
        "type": "verify",
        "exp": expire,
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
