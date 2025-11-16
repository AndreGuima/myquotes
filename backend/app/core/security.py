from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt

# Chave secreta — depois vamos mover para settings.py
SECRET_KEY = "MYQUOTES_SUPER_SECRET_KEY_123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Para hashing de senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============================================================
# 🔐 HASH / VERIFICAÇÃO DE SENHA
# ============================================================

def hash_password(password: str) -> str:
    """Gera hash seguro pra armazenar no banco."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compara senha enviada com hash salvo."""
    return pwd_context.verify(plain_password, hashed_password)


# ============================================================
# 🔐 JWT - CRIAR E VALIDAR TOKENS
# ============================================================

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Cria um token JWT assinado."""
    to_encode = data.copy()

    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def decode_access_token(token: str):
    """Valida e decodifica o token JWT."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        return None
