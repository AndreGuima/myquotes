# ✨ MyQuotes — Full-Stack Quotes App

> 📝 Aplicação completa para gerenciamento de frases com **FastAPI + React Native (Expo) + MySQL + Pytest + Docker**.  
> Focada em boas práticas, arquitetura simples e ambiente moderno de desenvolvimento.

<p align="center">
 <img src="https://img.shields.io/badge/python-3.13-blue" />
 <img src="https://img.shields.io/badge/fastapi-rocket-brightgreen" />
 <img src="https://img.shields.io/badge/react_native-expo-blueviolet" />
 <img src="https://img.shields.io/badge/pydantic-v2-success" />
 <img src="https://img.shields.io/badge/sqlalchemy-2.x-orange" />
 <img src="https://img.shields.io/badge/tests-100%25%20passing-brightgreen" />
 <img src="https://img.shields.io/badge/docker-compose-2496ED" />
</p>

---

# 📦 Stack Tecnológica

| Camada      | Tecnologias                                      |
|-------------|--------------------------------------------------|
| **Backend** | Python · FastAPI · SQLAlchemy · Pydantic v2      |
| **Database**| MySQL 8 (Docker)                                 |
| **Frontend**| Expo · React Native · Axios                      |
| **Testes**  | Pytest · SQLite in-memory · Overrides FastAPI    |
| **Infra**   | Docker Compose · Ambiente Virtual (venv)         |

---

# 🚀 Como Rodar o Projeto

## 🧠 Backend — API FastAPI

### ▶️ Ambiente Prod-like (Docker)

```bash
./scripts/start.sh
# ou
./scripts/start.sh --rebuild
```

### 🛠 Ambiente Dev (sem Docker)

```bash
docker compose up -d db

cd ~/MyQuotes
./backend/run-dev.sh
```

### 🧪 Rodar Testes (100% passando 🎉)

```bash
cd ~/MyQuotes
source backend/venv/bin/activate
pytest -v backend/tests/
```

➡️ API disponível em:  
**http://localhost:8000**  
**http://localhost:8000/docs** (Swagger)

---

## 📱 Frontend — Expo (React Native)

```bash
cd ~/MyQuotes/myquotes-web
npm install
npm run dev
```

Frontend disponível em:  
➡️ **http://localhost:5173**

---

# 🗂 Estrutura Geral do Projeto

```txt
MyQuotes/
│
├── backend/
│   ├── app/
│   │   ├── core/          # JWT, segurança e dependências
│   │   ├── routes/        # Endpoints (quotes, users, auth)
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic V2 schemas
│   │   ├── database.py    # Engine + SessionLocal
│   │   ├── settings.py    # Configuração via .env
│   │   └── main.py        # FastAPI app
│   ├── tests/             # Testes Pytest (SQLite em memória)
│   └── scripts/           # Scripts utilitários
│
├── myquotes-web/          # Frontend (React Native + Expo)
│
└── scripts/               # Docker / gerenciamento
```

---

# 🧹 Scripts Úteis

| Ação                  | Comando                      |
|----------------------|------------------------------|
| Start containers     | `./scripts/start.sh`         |
| Stop containers      | `./scripts/stop.sh`          |
| Status geral         | `./scripts/status.sh`        |
| Criar ambiente dev   | `./backend/run-dev.sh`       |
| Rodar testes         | `pytest -v backend/tests/`   |

---

# 🔐 Destaques Técnicos

- JWT + Bearer Token  
- Rotas protegidas por `get_current_user`  
- Permissões por usuário (admin, editor, user)  
- Banco de testes isolado (SQLite in-memory)  
- Testes rápidos com override de dependências  
- Estrutura moderna com Pydantic v2 + SQLAlchemy 2.x  
- Docker para ambiente de produção e desenvolvimento  

---

# 🤝 Contribuindo

Pull requests são bem-vindos!  
Fique à vontade para sugerir melhorias, refatorações ou novas features.

---

<p align="center">
 Feito com ❤️ café ☕ e muita dedicação.
</p>