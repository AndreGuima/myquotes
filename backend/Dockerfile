FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
      default-mysql-client \
      build-essential \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

RUN python3 -m pip install --upgrade pip

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY alembic.ini /app/alembic.ini
COPY migrations/ /app/migrations/

# ✅ Opção B correta
COPY app/ /app
COPY templates/ /app/templates/

COPY wait-for-db.sh /app/wait-for-db.sh
RUN chmod +x /app/wait-for-db.sh

RUN useradd -m appuser
USER appuser

EXPOSE 8000

CMD ["sh", "-c", "/app/wait-for-db.sh && alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]
