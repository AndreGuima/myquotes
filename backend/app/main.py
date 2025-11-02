
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import time
import logging

from .config import engine
from .models.quote import Base, Quote

logger = logging.getLogger("app.main")

app = FastAPI(title="MyQuotes API")

# Very permissive CORS for local development; adapt for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    # Try to connect to the database with a few retries before giving up.
    max_attempts = 10
    delay = 3  # seconds between attempts
    attempt = 0
    while attempt < max_attempts:
        try:
            # attempt a lightweight connection
            with engine.connect() as conn:
                logger.info("Database connection established on attempt %s", attempt + 1)
                break
        except Exception as e:
            attempt += 1
            logger.warning("Database not ready (attempt %s/%s): %s", attempt, max_attempts, e)
            time.sleep(delay)
    else:
        # All attempts failed; log error and continue startup (endpoints will fail on DB ops)
        logger.error("Could not connect to database after %s attempts; continuing without DB", max_attempts)
        return

    try:
        # Create tables if they don't exist (useful for local dev)
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables ensured (create_all completed)")
    except Exception:
        logger.exception("Failed to create tables during startup")


@app.get("/quotes")
def list_quotes():
    with Session(engine) as sess:
        quotes = sess.query(Quote).all()
        return [
            {
                "id": q.id,
                "author": q.author,
                "text": q.text,
                "created_at": q.created_at.isoformat() if q.created_at else None,
            }
            for q in quotes
        ]


@app.post("/quotes")
def create_quote(payload: dict):
    author = payload.get("author")
    text = payload.get("text")
    if not author or not text:
        raise HTTPException(status_code=400, detail="author and text are required")

    q = Quote(author=author, text=text)
    with Session(engine) as sess:
        sess.add(q)
        sess.commit()
        sess.refresh(q)
        return {"id": q.id, "author": q.author, "text": q.text}
