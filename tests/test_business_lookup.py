import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_business_lookup_success():
    response = client.post("/business/lookup", json={"phone": "6592701525"})
    assert response.status_code == 200
    assert response.json() == 96

def test_business_lookup_with_formatting():
    response = client.post("/business/lookup", json={"phone": "659-030-6703"})
    assert response.status_code == 200
    assert response.json() == 11

def test_business_lookup_not_found():
    response = client.post("/business/lookup", json={"phone": "0000000000"})
    assert response.status_code == 404

def test_business_lookup_invalid_input():
    # Test with missing phone field
    response = client.post("/business/lookup", json={})
    assert response.status_code == 422 # Validation error

def test_business_register_success():
    phone = "5556667777"
    biz_id = 999
    response = client.post("/business/register", json={"phone": phone, "business_id": biz_id})
    assert response.status_code == 200
    assert response.json()["message"] == "Mapping registered successfully"
    
    # Verify it can be looked up
    lookup_response = client.post("/business/lookup", json={"phone": phone})
    assert lookup_response.status_code == 200
    assert lookup_response.json() == biz_id

def test_business_register_duplicate_biz_id():
    # 96 is already assigned to 6592701525
    response = client.post("/business/register", json={"phone": "0001112222", "business_id": 96})
    assert response.status_code == 400
    assert "already assigned" in response.json()["detail"]

def test_business_register_same_phone_new_biz_id():
    # Updating an existing phone number with a new biz id (if biz id is free)
    phone = "6592701525"
    new_biz_id = 888
    response = client.post("/business/register", json={"phone": phone, "business_id": new_biz_id})
    assert response.status_code == 200
    
    lookup_response = client.post("/business/lookup", json={"phone": phone})
    assert lookup_response.json() == new_biz_id
