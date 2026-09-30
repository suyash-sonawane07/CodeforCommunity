import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import get_db

client = TestClient(app)

def test_signup_and_login():
    # Cleanup if exists
    # Signup
    res = client.post("/auth/signup", json={"email": "test2@demo.com", "password": "pass", "name": "Test"})
    assert res.status_code in [201, 400] # if already exists it's 400
    
    # Login
    res = client.post("/auth/login", json={"email": "test2@demo.com", "password": "pass"})
    assert res.status_code == 200
    token = res.json()["access_token"]
    
    # Role enforcement
    res = client.get("/stats", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403

def test_owner_only_request():
    # Login as test2@demo.com (user)
    res = client.post("/auth/login", json={"email": "test2@demo.com", "password": "pass"})
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create request
    res = client.post("/requests", json={"channel": "text", "text": "Help", "consent_ack": True}, headers=headers)
    req_id = res.json()["request_id"]
    
    # Can access own request
    res = client.get(f"/requests/{req_id}", headers=headers)
    assert res.status_code == 200
    
    # Signup another user
    client.post("/auth/signup", json={"email": "other2@demo.com", "password": "pass", "name": "Other"})
    res2 = client.post("/auth/login", json={"email": "other2@demo.com", "password": "pass"})
    token2 = res2.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    # Cannot access first user's request
    res = client.get(f"/requests/{req_id}", headers=headers2)
    assert res.status_code == 403
