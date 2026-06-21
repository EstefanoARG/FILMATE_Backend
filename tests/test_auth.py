from app.core.security import hash_password, verify_password
from app.repositories import user_repository


def test_register(client):
    payload = {
        "username": "testuser",
        "correo": "test@example.com",
        "contrasena": "Test1234!",
        "nombre": "Test User",
        "id_tipo_doc": 1,
        "numero_documento": "12345678",
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["correo"] == "test@example.com"
    assert "contrasena" not in data  # password not exposed


def test_register_duplicate_username(client, db):
    payload = {
        "username": "dupuser",
        "correo": "dup@example.com",
        "contrasena": "Test1234!",
        "nombre": "Dup User",
        "id_tipo_doc": 1,
        "numero_documento": "87654321",
    }
    client.post("/auth/register", json=payload)
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 400
    assert "email already registered" in response.json()["detail"].lower()


def test_login_success(client):
    payload = {
        "username": "loginuser",
        "correo": "login@example.com",
        "contrasena": "MyPass123!",
        "nombre": "Login User",
        "id_tipo_doc": 1,
        "numero_documento": "11111111",
    }
    client.post("/auth/register", json=payload)
    response = client.post("/auth/login", json={
        "correo": "login@example.com",
        "contrasena": "MyPass123!",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Login successful"
    assert data["user"]["correo"] == "login@example.com"


def test_login_wrong_password(client):
    payload = {
        "username": "wrongpass",
        "correo": "wrong@example.com",
        "contrasena": "Correct1!",
        "nombre": "Wrong Pass",
        "id_tipo_doc": 1,
        "numero_documento": "22222222",
    }
    client.post("/auth/register", json=payload)
    response = client.post("/auth/login", json={
        "correo": "wrong@example.com",
        "contrasena": "WrongPass!",
    })
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    response = client.post("/auth/login", json={
        "correo": "nobody@example.com",
        "contrasena": "SomePass1!",
    })
    assert response.status_code == 401


def test_hash_password():
    hashed = hash_password("SecurePass1!")
    assert hashed != "SecurePass1!"
    assert verify_password("SecurePass1!", hashed)


def test_verify_wrong_password():
    hashed = hash_password("RealPass1!")
    assert not verify_password("FakePass1!", hashed)
