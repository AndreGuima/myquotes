from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
import os

# Internos
from app.database import Base, engine
from app.routes.quotes import router as quotes_router
from app.routes.users import router as users_router
from app.settings import settings
from app.startup import create_default_admin
from app.routes.auth import router as auth_router


# ==========================================
# ⚙️ Lifespan moderno
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Inicializando MyQuotes API...")

    try:
        # 🔧 Garante que as tabelas existam
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas verificadas/criadas com sucesso.")

        # 👤 Cria admin padrão
        create_default_admin()

    except SQLAlchemyError as e:
        print(f"❌ Erro ao inicializar o banco: {e}")

    yield  # App rodando

    print("🛑 Encerrando MyQuotes API...")


# ==========================================
# 🚀 Instância principal do app
# ==========================================
# 🚀 Instância principal do app
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
        lifespan=lifespan,          # 👈 Só aqui usamos lifespan
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


# ==========================================
# ✅ Health Check
# ==========================================
@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "MyQuotes API is running 🚀"}
