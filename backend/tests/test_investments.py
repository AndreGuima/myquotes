from decimal import Decimal

import routes.investments as investments_routes
import services.investment_price_sync as investment_price_sync_service
from fastapi import HTTPException
from fastapi.testclient import TestClient
from services.brapi_client import BrapiQuote


def _mock_quotes_by_ticker(monkeypatch, price_by_ticker: dict[str, str | Decimal]):
    def fake_fetch_quotes(tickers: list[str]):
        results = {}
        for ticker in tickers:
            normalized = str(ticker).strip().upper()
            price = price_by_ticker.get(normalized)
            if price is None:
                continue
            results[normalized] = BrapiQuote(
                ticker=normalized,
                name=f"{normalized} Corp",
                regular_market_price=Decimal(str(price)),
                currency="BRL",
            )
        return results

    monkeypatch.setattr(investments_routes, "fetch_quotes", fake_fetch_quotes)
    monkeypatch.setattr(
        investment_price_sync_service, "fetch_quotes", fake_fetch_quotes
    )


def test_investments_crud_and_history(client: TestClient, monkeypatch):
    _mock_quotes_by_ticker(monkeypatch, {"PETR4": "31.52", "HGLG11": "167.89"})

    create_res = client.post(
        "/investments",
        json={
            "asset_type": "stock",
            "sector": "Energia",
            "ticker": "petr4",
            "name": "",
            "quantity": "10",
            "average_price": "28.45",
        },
    )
    assert create_res.status_code == 201
    created = create_res.json()
    assert created["ticker"] == "PETR4"
    assert created["name"] == "PETR4 Corp"
    assert created["current_price"] == "31.5200"
    assert created["price_updated_at"] is not None

    list_res = client.get("/investments")
    assert list_res.status_code == 200
    listed = list_res.json()
    assert len(listed) == 1
    assert listed[0]["current_price"] == "31.5200"

    update_res = client.patch(
        f"/investments/{created['id']}",
        json={
            "asset_type": "fii",
            "sector": "Logistica",
            "ticker": "hglg11",
            "quantity": "8",
            "average_price": "158.00",
        },
    )
    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["asset_type"] == "fii"
    assert updated["ticker"] == "HGLG11"
    assert updated["current_price"] == "167.8900"

    history_res = client.get(f"/investments/{created['id']}/price-history")
    assert history_res.status_code == 200
    history = history_res.json()
    assert len(history) == 2
    assert history[0]["ticker"] == "PETR4"
    assert history[0]["price"] == "31.5200"
    assert history[1]["ticker"] == "HGLG11"
    assert history[1]["price"] == "167.8900"

    delete_res = client.delete(f"/investments/{created['id']}")
    assert delete_res.status_code == 204

    list_after_delete_res = client.get("/investments")
    assert list_after_delete_res.status_code == 200
    assert list_after_delete_res.json() == []


def test_sync_investment_prices_endpoint(client: TestClient, monkeypatch):
    _mock_quotes_by_ticker(monkeypatch, {"VALE3": "54.10"})

    create_res = client.post(
        "/investments",
        json={
            "asset_type": "stock",
            "sector": "Mineracao",
            "ticker": "VALE3",
            "name": "Vale",
            "quantity": "5",
            "average_price": "50.00",
        },
    )
    assert create_res.status_code == 201
    investment_id = create_res.json()["id"]

    _mock_quotes_by_ticker(monkeypatch, {"VALE3": "55.25"})
    sync_res = client.post("/investments/sync-prices")
    assert sync_res.status_code == 200
    sync_payload = sync_res.json()
    assert sync_payload["synced_investments"] == 1
    assert sync_payload["synced_tickers"] == 1
    assert sync_payload["captured_at"] is not None

    list_res = client.get("/investments")
    assert list_res.status_code == 200
    assert list_res.json()[0]["current_price"] == "55.2500"

    history_res = client.get(f"/investments/{investment_id}/price-history?limit=10")
    assert history_res.status_code == 200
    history = history_res.json()
    assert len(history) == 2
    assert history[-1]["price"] == "55.2500"


def test_create_investment_allows_null_price_when_brapi_is_unavailable(
    client: TestClient, monkeypatch
):
    def failing_fetch_quotes(_tickers: list[str]):
        raise HTTPException(
            status_code=502,
            detail="Falha ao consultar cotação na BRAPI",
        )

    monkeypatch.setattr(investments_routes, "fetch_quotes", failing_fetch_quotes)
    monkeypatch.setattr(
        investment_price_sync_service,
        "fetch_quotes",
        failing_fetch_quotes,
    )

    create_res = client.post(
        "/investments",
        json={
            "asset_type": "stock",
            "sector": "Energia",
            "ticker": "PETR4",
            "name": "Petrobras",
            "quantity": "10",
            "average_price": "28.45",
        },
    )
    assert create_res.status_code == 201
    created = create_res.json()
    assert created["current_price"] is None
    assert created["price_updated_at"] is None


def test_sync_investment_prices_returns_empty_result_when_brapi_is_unavailable(
    client: TestClient, monkeypatch
):
    _mock_quotes_by_ticker(monkeypatch, {"VALE3": "54.10"})

    create_res = client.post(
        "/investments",
        json={
            "asset_type": "stock",
            "sector": "Mineracao",
            "ticker": "VALE3",
            "name": "Vale",
            "quantity": "5",
            "average_price": "50.00",
        },
    )
    assert create_res.status_code == 201

    def failing_fetch_quotes(_tickers: list[str]):
        raise HTTPException(
            status_code=502,
            detail="Falha ao consultar cotação na BRAPI",
        )

    monkeypatch.setattr(investments_routes, "fetch_quotes", failing_fetch_quotes)
    monkeypatch.setattr(
        investment_price_sync_service,
        "fetch_quotes",
        failing_fetch_quotes,
    )

    sync_res = client.post("/investments/sync-prices")
    assert sync_res.status_code == 200
    payload = sync_res.json()
    assert payload["synced_investments"] == 0
    assert payload["synced_tickers"] == 0
    assert payload["captured_at"] is not None
