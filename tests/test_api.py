
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200

def test_analyze_rejects_unknown():
    files = {"file": ("a.txt", b"hello", "text/plain")}
    r = client.post("/analyze", files=files)
    assert r.status_code == 400
