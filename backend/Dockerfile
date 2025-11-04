FROM python:3.12-slim

WORKDIR /app

# Install MySQL client + system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
      default-mysql-client \
      build-essential \
    && rm -rf /var/lib/apt/lists/*

# Optimize Python runtime behavior
ENV PYTHONUNBUFFERED=1

# Upgrade pip
RUN python3 -m pip install --upgrade pip

# Copy dependency list
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code after deps
COPY . .

# Ensure wait script is executable
RUN chmod +x /app/wait-for-db.sh

# Security: run as non-root
RUN useradd -m appuser
USER appuser

EXPOSE 8000

CMD ["sh", "-c", "./wait-for-db.sh && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]
