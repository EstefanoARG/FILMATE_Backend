def _create_test_user(db):
    from app.models.user import Usuario
    from app.core.security import hash_password

    user = Usuario(
        username="movietestuser",
        correo="movietest@example.com",
        contrasena=hash_password("Test1234!"),
        nombre="Movie Test User",
        id_tipo_doc=1,
        numero_documento="33333333",
        estado_usuario="Activo",
    )
    db.add(user)
    db.commit()
    return user.id_usuario


def test_get_user(client, db):
    user_id = _create_test_user(db)
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "movietestuser"
    assert data["correo"] == "movietest@example.com"


def test_get_user_not_found(client):
    response = client.get("/users/99999")
    assert response.status_code == 404


def test_update_user(client, db):
    user_id = _create_test_user(db)
    response = client.put(f"/users/{user_id}", json={"nombre": "Updated Name"})
    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Updated Name"


def test_search_users(client, db):
    _create_test_user(db)
    response = client.get("/users/search", params={"q": "movietest"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


def test_search_users_no_match(client):
    response = client.get("/users/search", params={"q": "zzzNoMatchzzz"})
    assert response.status_code == 200
    assert response.json() == []
