"""
Job: Sincroniza cotações de investimentos no banco.
"""

import logging
import time
from datetime import datetime, timezone

from core.logging_config import setup_logging
from database import SessionLocal
from services.investment_price_sync import sync_investment_prices
from services.job_run_service import create_job_run, finish_job_run

setup_logging()
logger = logging.getLogger("app.cron.sync_investment_prices")
JOB_NAME = "sync_investment_prices"


def main():
    db = SessionLocal()
    started_at = datetime.now(timezone.utc)
    perf_started_at = time.perf_counter()
    job_run = None
    try:
        job_run = create_job_run(
            db,
            job_name=JOB_NAME,
        )
        db.commit()
        synced_investments, synced_tickers, captured_at = sync_investment_prices(db)
        duration_ms = int((time.perf_counter() - perf_started_at) * 1000)
        finish_job_run(
            db,
            job_run,
            status="success",
            started_at=started_at,
            meta_json={
                "synced_investments": synced_investments,
                "synced_tickers": synced_tickers,
                "captured_at": captured_at.isoformat(),
            },
        )
        db.commit()
        logger.info(
            "sync_prices_success",
            extra={
                "job_name": JOB_NAME,
                "status": "success",
                "synced_investments": synced_investments,
                "synced_tickers": synced_tickers,
                "duration_ms": duration_ms,
                "captured_at": captured_at.isoformat(),
            },
        )
    except Exception:
        db.rollback()
        if job_run is not None:
            try:
                finish_job_run(
                    db,
                    job_run,
                    status="failed",
                    started_at=started_at,
                    meta_json={},
                )
                db.commit()
            except Exception:
                db.rollback()

        logger.exception(
            "sync_prices_failed",
            extra={
                "job_name": JOB_NAME,
                "status": "failed",
                "duration_ms": int((time.perf_counter() - perf_started_at) * 1000),
            },
        )
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
