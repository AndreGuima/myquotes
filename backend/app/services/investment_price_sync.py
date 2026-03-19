from __future__ import annotations

from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal

from models.investment import Investment
from models.investment_price_history import InvestmentPriceHistory
from services.brapi_client import fetch_quotes
from sqlalchemy.orm import Session


def _to_price_decimal(value: object) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def sync_investment_prices(
    db: Session,
    *,
    user_id: int | None = None,
    investment_ids: list[int] | None = None,
    quotes_by_ticker: dict | None = None,
) -> tuple[int, int, datetime]:
    query = db.query(Investment)
    if user_id is not None:
        query = query.filter(Investment.user_id == user_id)
    if investment_ids:
        query = query.filter(Investment.id.in_(investment_ids))

    investments = query.order_by(Investment.id.asc()).all()
    if not investments:
        captured_at = datetime.now(timezone.utc)
        return 0, 0, captured_at

    quotes = quotes_by_ticker or fetch_quotes([item.ticker for item in investments])
    captured_at = datetime.now(timezone.utc)
    synced_investments = 0
    synced_tickers: set[str] = set()

    for investment in investments:
        quote = quotes.get(investment.ticker.strip().upper())
        if quote is None:
            continue

        price = _to_price_decimal(quote.regular_market_price)
        investment.current_price = price
        investment.price_updated_at = captured_at
        if not investment.name.strip():
            investment.name = quote.name

        db.add(
            InvestmentPriceHistory(
                user_id=investment.user_id,
                investment_id=investment.id,
                ticker=investment.ticker,
                price=price,
                currency=quote.currency,
                source="brapi",
                captured_at=captured_at,
            )
        )
        synced_investments += 1
        synced_tickers.add(investment.ticker.strip().upper())

    db.flush()
    return synced_investments, len(synced_tickers), captured_at
