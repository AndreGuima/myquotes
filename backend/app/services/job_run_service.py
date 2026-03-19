from __future__ import annotations

from datetime import datetime, timezone

from models.job_run import JobRun
from sqlalchemy.orm import Session


def create_job_run(
    db: Session,
    *,
    job_name: str,
    meta_json: dict | None = None,
) -> JobRun:
    job_run = JobRun(
        job_name=job_name,
        status="running",
        started_at=datetime.now(timezone.utc),
        meta_json=meta_json,
    )
    db.add(job_run)
    db.flush()
    return job_run


def finish_job_run(
    db: Session,
    job_run: JobRun,
    *,
    status: str,
    started_at: datetime,
    meta_json: dict | None = None,
) -> JobRun:
    finished_at = datetime.now(timezone.utc)
    duration_ms = max(
        0,
        int((finished_at - started_at).total_seconds() * 1000),
    )

    job_run.status = status
    job_run.finished_at = finished_at
    job_run.duration_ms = duration_ms
    if meta_json is not None:
        job_run.meta_json = meta_json

    db.add(job_run)
    db.flush()
    return job_run
