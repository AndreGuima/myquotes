from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Request, status
from models.auth_login_attempt import AuthLoginAttempt
from settings import settings
from sqlalchemy.orm import Session


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def get_client_ip(request: Request) -> str:
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def _get_or_create_attempt(
    db: Session, email: str, ip_address: str
) -> AuthLoginAttempt:
    normalized_email = _normalize_email(email)
    attempt = (
        db.query(AuthLoginAttempt)
        .filter(
            AuthLoginAttempt.email == normalized_email,
            AuthLoginAttempt.ip_address == ip_address,
        )
        .first()
    )

    if not attempt:
        attempt = AuthLoginAttempt(
            email=normalized_email,
            ip_address=ip_address,
            attempts=0,
            last_attempt_at=None,
            locked_until=None,
        )
        db.add(attempt)
        db.commit()
        db.refresh(attempt)

    return attempt


def _get_attempt(db: Session, email: str, ip_address: str) -> AuthLoginAttempt | None:
    normalized_email = _normalize_email(email)
    return (
        db.query(AuthLoginAttempt)
        .filter(
            AuthLoginAttempt.email == normalized_email,
            AuthLoginAttempt.ip_address == ip_address,
        )
        .first()
    )


def _to_aware_utc(value: datetime | None) -> datetime | None:
    if not value:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _reset_if_window_expired(attempt: AuthLoginAttempt, now: datetime) -> None:
    window_seconds = settings.BRUTE_FORCE_WINDOW_SECONDS
    last_attempt = _to_aware_utc(attempt.last_attempt_at)
    if last_attempt and last_attempt < now - timedelta(seconds=window_seconds):
        attempt.attempts = 0
        attempt.locked_until = None
        attempt.last_attempt_at = None


def enforce_bruteforce_limit(db: Session, email: str, ip_address: str) -> None:
    """
    Raises HTTP 429 if user/ip is currently locked.
    """
    now = datetime.now(timezone.utc)
    attempt = _get_attempt(db, email, ip_address)
    if not attempt:
        return

    _reset_if_window_expired(attempt, now)

    locked_until = _to_aware_utc(attempt.locked_until)
    if locked_until and locked_until > now:
        retry_after_seconds = int((locked_until - now).total_seconds())
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Muitas tentativas. Tente novamente mais tarde.",
            headers={"Retry-After": str(max(retry_after_seconds, 1))},
        )


def register_failed_login(db: Session, email: str, ip_address: str) -> bool:
    """
    Returns True if this failure triggered a lockout.
    """
    now = datetime.now(timezone.utc)
    attempt = _get_or_create_attempt(db, email, ip_address)

    _reset_if_window_expired(attempt, now)

    attempt.attempts += 1
    attempt.last_attempt_at = now

    locked = False
    if attempt.attempts >= settings.BRUTE_FORCE_MAX_ATTEMPTS:
        attempt.locked_until = now + timedelta(
            seconds=settings.BRUTE_FORCE_LOCKOUT_SECONDS
        )
        locked = True

    db.commit()
    return locked


def clear_login_attempts(db: Session, email: str, ip_address: str) -> None:
    normalized_email = _normalize_email(email)
    attempt = (
        db.query(AuthLoginAttempt)
        .filter(
            AuthLoginAttempt.email == normalized_email,
            AuthLoginAttempt.ip_address == ip_address,
        )
        .first()
    )
    if not attempt:
        return

    attempt.attempts = 0
    attempt.last_attempt_at = None
    attempt.locked_until = None
    db.commit()
