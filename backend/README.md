# MyQuotes - backend (FastAPI)

Quickstart for the backend (FastAPI) used in this project.

Prerequisites
- Python 3.10+ (use the project's virtualenv)
- A running MySQL instance (the project includes a docker-compose service)

Setup

1. Activate the virtualenv

```bash
source venv/bin/activate
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Copy environment file and adapt values (do NOT commit `.env`)

```bash
cp .env.example .env
# edit .env if needed
```

4. Run the app locally

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API

- GET /quotes  — list quotes
- POST /quotes — create a quote (JSON: {"author": "..", "text": ".."})

Notes
- The scaffold uses SQLAlchemy and will create the `quotes` table on startup if it does not exist (useful for local dev).
- For production, prefer managed migrations (Alembic) and secure handling of credentials.
