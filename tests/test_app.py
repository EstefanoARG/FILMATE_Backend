from app.core.database import Base


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Filmate" in data["message"]


def test_openapi(client):
    response = client.get("/api/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "Filmate API"
    assert "/client/movies/" in str(schema["paths"])
    assert "/admin/movies/" in str(schema["paths"])
    assert "/auth/register" in str(schema["paths"])
