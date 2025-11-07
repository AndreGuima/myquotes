#!/usr/bin/env bash
set -e

# Go to backend directory
cd "$(dirname "$0")"

# Activate virtualenv
source venv/bin/activate

# Load dev environment variables
export $(grep -v '^#' .env.dev | xargs)

echo "✅ Running FastAPI in DEV mode with .env.dev"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
