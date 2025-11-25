FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
      default-mysql-client \
      build-essential \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1

RUN python3 -m pip install --upgrade pip

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY alembic.ini /app/alembic.ini
COPY migrations /app/migrations

# Copiar apenas o backend, não o diretório inteiro
COPY app /app/src/app
COPY wait-for-db.sh /app/src/wait-for-db.sh

ENV PYTHONPATH="/app/src"

RUN chmod +x /app/src/wait-for-db.sh

RUN useradd -m appuser
USER appuser

EXPOSE 8000

CMD ["sh", "-c", "/app/src/wait-for-db.sh && uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --reload"]
