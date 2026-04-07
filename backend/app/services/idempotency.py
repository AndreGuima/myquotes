import hashlib
import json

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from models.idempotency_key import IdempotencyKey
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


def _build_request_hash(payload: object) -> str:
    serialized = json.dumps(
        jsonable_encoder(payload),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def begin_idempotent_request(
    db: Session,
    *,
    user_id: int,
    route_key: str,
    idempotency_key: str | None,
    payload: object,
) -> tuple[IdempotencyKey | None, JSONResponse | None]:
    if not idempotency_key:
        return None, None

    request_hash = _build_request_hash(payload)
    record = IdempotencyKey(
        user_id=user_id,
        route_key=route_key,
        idempotency_key=idempotency_key,
        request_hash=request_hash,
    )
    db.add(record)
    try:
        db.flush()
        return record, None
    except IntegrityError:
        db.rollback()
        existing = (
            db.query(IdempotencyKey)
            .filter(
                IdempotencyKey.user_id == user_id,
                IdempotencyKey.route_key == route_key,
                IdempotencyKey.idempotency_key == idempotency_key,
            )
            .first()
        )
        if not existing:
            raise
        if existing.request_hash != request_hash:
            raise HTTPException(
                status_code=409,
                detail="Idempotency-Key já utilizado com payload diferente",
            )
        if existing.response_body is None or existing.status_code is None:
            raise HTTPException(
                status_code=409,
                detail="Requisição idempotente já está em processamento",
            )
        return None, JSONResponse(
            status_code=existing.status_code,
            content=json.loads(existing.response_body),
        )


def finalize_idempotent_request(
    db: Session,
    *,
    record: IdempotencyKey | None,
    response_body: object,
    status_code: int,
) -> None:
    if record is None:
        return
    record.response_body = json.dumps(
        jsonable_encoder(response_body),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    record.status_code = status_code
    db.flush()
