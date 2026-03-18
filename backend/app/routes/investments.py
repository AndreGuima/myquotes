from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal

from core.dependencies import get_current_user
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query, status
from models.investment import Investment
from models.investment_price_history import InvestmentPriceHistory
from models.user import User
from schemas.investment import (
    InvestmentCreate,
    InvestmentPriceHistoryRead,
    InvestmentPriceSyncResult,
    InvestmentRead,
    InvestmentUpdate,
)
from services.brapi_client import fetch_quotes
from services.investment_price_sync import sync_investment_prices
from sqlalchemy.orm import Session

router = APIRouter(prefix="/investments", tags=["Investments"])


def _to_money_decimal(value: object) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def _normalize_text(value: str | None) -> str:
    return str(value or "").strip()


def _normalize_ticker(value: str) -> str:
    ticker = _normalize_text(value).upper()
    if not ticker:
        raise HTTPException(status_code=400, detail="Ticker é obrigatório")
    return ticker


def _to_response(item: Investment) -> InvestmentRead:
    return InvestmentRead(
        id=item.id,
        asset_type=item.asset_type,
        sector=item.sector or "",
        ticker=item.ticker,
        name=item.name,
        quantity=item.quantity,
        average_price=item.average_price,
        current_price=item.current_price,
        price_updated_at=item.price_updated_at,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _fetch_quote_if_available(ticker: str):
    try:
        return fetch_quotes([ticker]).get(ticker), None
    except HTTPException as exc:
        if exc.status_code >= 500:
            return None, exc
        raise


def _get_user_investment_or_404(
    db: Session, user_id: int, investment_id: int
) -> Investment:
    item = (
        db.query(Investment)
        .filter(Investment.id == investment_id, Investment.user_id == user_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Investimento não encontrado")
    return item


@router.get("", response_model=list[InvestmentRead])
def list_investments(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    items = (
        db.query(Investment)
        .filter(Investment.user_id == user.id)
        .order_by(Investment.ticker.asc(), Investment.id.asc())
        .all()
    )
    return [_to_response(item) for item in items]


@router.post("", status_code=status.HTTP_201_CREATED, response_model=InvestmentRead)
def create_investment(
    payload: InvestmentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ticker = _normalize_ticker(payload.ticker)
    quote, fetch_error = _fetch_quote_if_available(ticker)
    if quote is None and fetch_error is None:
        raise HTTPException(status_code=400, detail="Ticker não encontrado na BRAPI")

    item = Investment(
        user_id=user.id,
        asset_type=payload.asset_type,
        sector=_normalize_text(payload.sector),
        ticker=ticker,
        name=_normalize_text(payload.name) or (quote.name if quote else ticker),
        quantity=_to_money_decimal(payload.quantity),
        average_price=_to_money_decimal(payload.average_price),
        current_price=(
            _to_money_decimal(quote.regular_market_price) if quote is not None else None
        ),
    )
    db.add(item)
    db.flush()

    if quote is not None:
        synced_investments, _, _ = sync_investment_prices(
            db,
            user_id=user.id,
            investment_ids=[item.id],
            quotes_by_ticker={ticker: quote},
        )
        if synced_investments == 0:
            raise HTTPException(status_code=502, detail="Falha ao sincronizar cotação")

    db.commit()
    db.refresh(item)
    return _to_response(item)


@router.patch("/{investment_id}", response_model=InvestmentRead)
def update_investment(
    investment_id: int,
    payload: InvestmentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    item = _get_user_investment_or_404(db, user.id, investment_id)
    ticker_changed = False

    if payload.asset_type is not None:
        item.asset_type = payload.asset_type
    if payload.sector is not None:
        item.sector = _normalize_text(payload.sector)
    if payload.ticker is not None:
        next_ticker = _normalize_ticker(payload.ticker)
        ticker_changed = next_ticker != item.ticker
        item.ticker = next_ticker
    if payload.name is not None:
        item.name = _normalize_text(payload.name)
    if payload.quantity is not None:
        item.quantity = _to_money_decimal(payload.quantity)
    if payload.average_price is not None:
        item.average_price = _to_money_decimal(payload.average_price)

    quote = None
    fetch_error = None
    if ticker_changed or payload.ticker is not None:
        quote, fetch_error = _fetch_quote_if_available(item.ticker)
        if quote is None and fetch_error is None:
            raise HTTPException(
                status_code=400, detail="Ticker não encontrado na BRAPI"
            )
        if not item.name:
            item.name = quote.name if quote is not None else item.ticker
        if quote is None and ticker_changed:
            item.current_price = None
            item.price_updated_at = None

    if quote is not None:
        sync_investment_prices(
            db,
            user_id=user.id,
            investment_ids=[item.id],
            quotes_by_ticker={item.ticker: quote},
        )
    db.commit()
    db.refresh(item)
    return _to_response(item)


@router.delete("/{investment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_investment(
    investment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    item = _get_user_investment_or_404(db, user.id, investment_id)
    db.delete(item)
    db.commit()
    return None


@router.get(
    "/{investment_id}/price-history",
    response_model=list[InvestmentPriceHistoryRead],
)
def get_investment_price_history(
    investment_id: int,
    limit: int = Query(default=90, ge=1, le=500),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _get_user_investment_or_404(db, user.id, investment_id)
    items = (
        db.query(InvestmentPriceHistory)
        .filter(
            InvestmentPriceHistory.user_id == user.id,
            InvestmentPriceHistory.investment_id == investment_id,
        )
        .order_by(
            InvestmentPriceHistory.captured_at.desc(), InvestmentPriceHistory.id.desc()
        )
        .limit(limit)
        .all()
    )
    return list(
        reversed([InvestmentPriceHistoryRead.model_validate(item) for item in items])
    )


@router.post("/sync-prices", response_model=InvestmentPriceSyncResult)
def sync_current_user_investment_prices(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        synced_investments, synced_tickers, captured_at = sync_investment_prices(
            db, user_id=user.id
        )
        db.commit()
    except HTTPException as exc:
        db.rollback()
        if exc.status_code < 500:
            raise

        synced_investments = 0
        synced_tickers = 0
        captured_at = datetime.now(timezone.utc)

    return InvestmentPriceSyncResult(
        synced_investments=synced_investments,
        synced_tickers=synced_tickers,
        captured_at=captured_at,
    )
