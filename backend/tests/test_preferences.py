# ============================================================
# Tests - Preferences
# ============================================================


def test_get_preferences_empty(client):
    """
    GET deve retornar objeto vazio se preferências ainda não existirem
    """
    response = client.get("/preferences/notifications")

    assert response.status_code == 200

    data = response.json()
    assert data["category"] == "notifications"
    assert data["preferences"] == {}


def test_put_preferences_creates_preferences(client):
    """
    PUT deve criar preferências se ainda não existirem
    """
    payload = {
        "preferences": {
            "email_enabled": True,
            "daily_quote": True,
        }
    }

    response = client.put(
        "/preferences/notifications",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()
    assert data["preferences"]["email_enabled"] is True
    assert data["preferences"]["daily_quote"] is True


def test_put_preferences_merges_preferences(client):
    """
    PUT deve fazer merge e não sobrescrever preferências existentes
    """
    # Criação inicial
    client.put(
        "/preferences/notifications",
        json={
            "preferences": {
                "email_enabled": True,
            }
        },
    )

    # Atualização parcial
    response = client.put(
        "/preferences/notifications",
        json={
            "preferences": {
                "daily_quote": False,
            }
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["preferences"]["email_enabled"] is True
    assert data["preferences"]["daily_quote"] is False


def test_put_preferences_empty_payload_returns_400(client):
    """
    PUT com payload vazio deve retornar 400
    """
    response = client.put(
        "/preferences/notifications",
        json={"preferences": {}},
    )

    assert response.status_code == 400
