# tests/test_api.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_order_flow():
    # Test order creation
    response = client.post("/orders/", json={...})
    assert response.status_code == 200
    
    # Test batch creation
    response = client.post("/batches/create", json={...})
    assert response.status_code == 200