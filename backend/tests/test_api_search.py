from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_search_endpoint():
    response = client.get("/api/search?q=训练")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data

def test_search_empty_query():
    response = client.get("/api/search")
    assert response.status_code == 422  # Validation error
