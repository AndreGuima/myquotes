import pytest
from core.security import validate_and_hash_password, validate_password_strength
from fastapi import HTTPException


def test_password_too_short():
    with pytest.raises(HTTPException) as exc:
        validate_password_strength("Ab1!")

    assert exc.value.status_code == 422
    assert "mínimo" in exc.value.detail


def test_password_missing_uppercase():
    with pytest.raises(HTTPException) as exc:
        validate_password_strength("abc123!@")

    assert "maiúscula" in exc.value.detail


def test_password_missing_lowercase():
    with pytest.raises(HTTPException) as exc:
        validate_password_strength("ABC123!@")

    assert "minúscula" in exc.value.detail


def test_password_missing_digit():
    with pytest.raises(HTTPException) as exc:
        validate_password_strength("Abcdef!@")

    assert "número" in exc.value.detail


def test_password_missing_special_char():
    with pytest.raises(HTTPException) as exc:
        validate_password_strength("Abcdef12")

    assert "especial" in exc.value.detail


def test_valid_password_passes_and_hashes():
    hashed = validate_and_hash_password("Abcdef12!")

    assert isinstance(hashed, str)
    assert hashed != "Abcdef12!"


def test_register_rejects_weak_password(client):
    payload = {
        "username": "weakuser",
        "email": "weak@example.com",
        "password": "12345678",
        "confirm_password": "12345678",
    }

    r = client.post("/auth/register", json=payload)

    assert r.status_code == 422
    assert "senha deve conter" in r.json()["detail"].lower()
