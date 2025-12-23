FROM python:3.12-slim

WORKDIR /app

# -------------------------
# System deps
# -------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
      default-mysql-client \
      build-essential \
      cron \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

RUN python3 -m pip install --upgrade pip

# -------------------------
# Python deps
# -------------------------
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# -------------------------
# App files
# -------------------------
COPY alembic.ini /app/alembic.ini
COPY migrations/ /app/migrations/
COPY app/ /app
COPY templates/ /app/templates/

COPY wait-for-db.sh /app/wait-for-db.sh
RUN chmod +x /app/wait-for-db.sh

# -------------------------
# Cron via cron.d
# -------------------------
COPY cron/daily_quote /etc/cron.d/daily_quote
RUN chmod 0644 /etc/cron.d/daily_quote \
    && chown root:root /etc/cron.d/daily_quote \
    && sed -i -e '$a\' /etc/cron.d/daily_quote \
    && touch /var/log/cron.log

# -------------------------
# User (ONLY for app)
# -------------------------
RUN useradd -m appuser \
    && chown -R appuser:appuser /app /var/log/cron.log

EXPOSE 8000

# -------------------------
# Start
# -------------------------
CMD ["sh", "-c", "/app/wait-for-db.sh && alembic upgrade head && su appuser -c \"uvicorn main:app --host 0.0.0.0 --port 8000\""]


