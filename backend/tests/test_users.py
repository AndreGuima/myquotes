def test_list_users(admin_client):
    r = admin_client.get("/admin/users/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert len(r.json()) == 1


def test_update_user(admin_client):
    payload = {
        "username": "admin-editado",
        "email": "admin-editado@example.com",
        "role": "admin",
    }

    r = admin_client.put("/admin/users/1", json=payload)

    assert r.status_code == 200
    data = r.json()
    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]
    assert data["role"] == payload["role"]


def test_deactivate_and_restore_user(admin_client):
    r = admin_client.delete("/admin/users/1")
    assert r.status_code == 200

    r = admin_client.get("/admin/users/")
    assert r.status_code == 200
    users = r.json()
    assert users[0]["is_active"] is False

    r = admin_client.post("/admin/users/1/restore")
    assert r.status_code == 200

    r = admin_client.get("/admin/users/")
    assert r.status_code == 200
    users = r.json()
    assert users[0]["is_active"] is True
