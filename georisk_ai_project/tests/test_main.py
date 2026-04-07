def test_healthcheck():
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200