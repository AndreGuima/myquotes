from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

import requests
from fastapi import HTTPException
from settings import settings


@dataclass
class BrapiQuote:
    ticker: str
    name: str
    regular_market_price: Decimal
    currency: str


def _build_headers() -> dict[str, str]:
    headers = {"Accept": "application/json"}
    if settings.BRAPI_TOKEN:
        headers["Authorization"] = f"Bearer {settings.BRAPI_TOKEN}"
    return headers


def _batched(values: list[str], size: int) -> list[list[str]]:
    return [values[index : index + size] for index in range(0, len(values), size)]


def fetch_quotes(tickers: list[str]) -> dict[str, BrapiQuote]:
    normalized = sorted(
        {str(ticker or "").strip().upper() for ticker in tickers if ticker}
    )
    if not normalized:
        return {}

    results: dict[str, BrapiQuote] = {}
    batch_size = max(1, int(settings.BRAPI_MAX_QUOTES_PER_REQUEST))
    for batch in _batched(normalized, batch_size):
        endpoint = f"{settings.BRAPI_BASE_URL.rstrip('/')}/api/quote/{','.join(batch)}"
        try:
            response = requests.get(
                endpoint,
                headers=_build_headers(),
                timeout=20,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            detail = "Falha ao consultar cotação na BRAPI"
            response = getattr(exc, "response", None)
            if response is not None:
                try:
                    payload = response.json()
                except ValueError:
                    payload = None

                message = payload.get("message") if isinstance(payload, dict) else None
                if isinstance(message, str) and message.strip():
                    detail = f"{detail}: {message.strip()}"
            raise HTTPException(
                status_code=502,
                detail=detail,
            ) from exc

        payload = response.json()
        for item in payload.get("results", []):
            ticker = str(item.get("symbol") or item.get("stock") or "").strip().upper()
            raw_price = item.get("regularMarketPrice")
            if not ticker or raw_price in (None, ""):
                continue
            name = (
                str(item.get("longName") or item.get("shortName") or ticker).strip()
                or ticker
            )
            results[ticker] = BrapiQuote(
                ticker=ticker,
                name=name,
                regular_market_price=Decimal(str(raw_price)),
                currency=str(item.get("currency") or "BRL").strip() or "BRL",
            )

    return results
