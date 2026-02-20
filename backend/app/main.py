import logging
import os
from contextlib import asynccontextmanager

# Internos
from core.logging_config import setup_logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.admin_users import router as admin_users_router
from routes.auth import router as auth_router
from routes.auth_forgot_password import router as forgot_password_router
from routes.auth_reset_password import router as reset_password_router
from routes.bank_accounts import router as bank_accounts_router
from routes.credit_cards import router as credit_cards_router
from routes.dreams import router as dreams_router
from routes.expense_categories import router as expense_categories_router
from routes.expenses import router as expenses_router
from routes.habits import router as habits_router
from routes.preferences import router as preferences_router
from routes.quotes import router as quotes_router
from routes.reading_list import router as reading_list_router
from routes.users import router as users_router
from sqlalchemy.exc import SQLAlchemyError
from startup import create_default_admin

# ==========================================
# ⚙️ Inicialização do logging (ANTES de tudo)
# ==========================================
setup_logging()
logger = logging.getLogger("app.startup")


# ==========================================
# ⚙️ Lifespan moderno
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Inicializando MyQuotes API")

    try:
        # 👤 Cria admin padrão
        create_default_admin()
        logger.info("Verificação/criação de admin padrão concluída")

    except SQLAlchemyError:
        logger.exception("Erro ao inicializar o banco de dados")

    yield  # App rodando

    logger.info("Encerrando MyQuotes API")


# ==========================================
# 🚀 Instância principal do app
# ==========================================
if os.getenv("TESTING") == "1":
    # Durante os testes: SEM lifespan
    app = FastAPI(
        title="MyQuotes API",
        description="API para gerenciar frases e usuários do projeto MyQuotes.",
        version="1.0.0",
    )
else:
    # Em produção / docker: lifespan ativo
    app = FastAPI(
        title="MyQuotes API",
        description="API para gerenciar frases e usuários do projeto MyQuotes.",
        version="1.0.0",
        contact={"name": "André Guimarães", "email": "andre@example.com"},
        license_info={"name": "MIT License"},
        lifespan=lifespan,
    )

# ==========================================
# 🌐 CORS Middleware
# ==========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 🔗 Registro de rotas
# ==========================================
app.include_router(users_router)
app.include_router(quotes_router)
app.include_router(auth_router)
app.include_router(admin_users_router)
app.include_router(preferences_router)
app.include_router(forgot_password_router)
app.include_router(reset_password_router)
app.include_router(reading_list_router)
app.include_router(dreams_router)
app.include_router(bank_accounts_router)
app.include_router(credit_cards_router)
app.include_router(expense_categories_router)
app.include_router(expenses_router)
app.include_router(
    habits_router,
    prefix="/habits",
    tags=["Habits"],
)


# ==========================================
# ✅ Health Check
# ==========================================
@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "MyQuotes API is running 🚀"}
