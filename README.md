# ✨ MyLife — Full-Stack Life Manager App

> 📝 Aplicação completa para gerenciamento de habitos feita com **FastAPI + React Native + MySQL + Pytest + Docker + Kubernetes**.  
> Focada em boas práticas e ambiente moderno de desenvolvimento.

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
cd ~/repo/myquotes
./scripts/start.sh
# ou
cd ~/repo/myquotes
./scripts/start.sh --rebuild
```

Esse fluxo sobe:

- `db` (MySQL 8)
- `backend` (FastAPI + migrations automáticas)
- `cron` (jobs agendados)
- `frontend` (build Vite servido por Nginx)

URLs locais:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

### 📱 Acessar pelo celular na mesma rede Wi‑Fi

O jeito correto no modo Docker é abrir o frontend no IP do seu computador. O Nginx do frontend faz proxy de `/api` para o backend, então o celular não precisa falar direto com a porta `8000`.

1. Descubra o IP local do seu computador:

```bash
hostname -I
```

ou:

```bash
ip addr show
```

2. Suba o ambiente:

```bash
cd ~/repo/myquotes
./scripts/start.sh --rebuild
```

3. No celular, abra:

```text
http://SEU_IP_LOCAL:5173
```

Exemplo:

```text
http://192.168.1.25:5173
```

4. Se não abrir, libere no firewall do computador as portas `5173` e `8000`.

Observação importante:

- Para navegação normal no app via celular, basta acessar `http://SEU_IP_LOCAL:5173`.
- Se você usa links enviados por e-mail, como reset de senha, ajuste `FRONTEND_URL` no arquivo `.env` para o IP da sua máquina, por exemplo `http://192.168.1.25:5173`, e depois rode `./scripts/restart.sh --rebuild`.

### 🧪 Rodar Testes

```bash
cd ~/repo/myquotes
source venv/bin/activate
pip install -r backend/requirements.txt
pytest -v backend/tests/
```

➡️ API disponível em:
**http://localhost:8000**
**http://localhost:8000/docs** (Swagger)

---

## 📱 Frontend — Expo (React Native)

```bash
cd ~/repo/myquotes/myquotes-web
npm install
npm run dev
```

Frontend disponível em:  
➡️ **http://localhost:5173**

---

# 🧹 Scripts Úteis

| Ação                  | Comando                      |
|----------------------|------------------------------|
| Start containers     | `./scripts/start.sh`         |
| Stop containers      | `./scripts/stop.sh`          |
| Status geral         | `./scripts/status.sh`        |
| Criar ambiente dev   | `./backend/run-dev.sh`       |
| Rodar testes         | `pytest -v backend/tests/`   |


<p align="center">
 Feito com ❤️ café ☕ e muita dedicação.
</p>
