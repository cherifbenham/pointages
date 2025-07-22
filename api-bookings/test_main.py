
from fastapi.testclient import TestClient
from main import app

def test_post_pointage():
    client = TestClient(app)
    payload = {
        "name": "Jane Doe",
        "type_sollicitation": "EXPERTISE",
        "practice": "Weekly",
        "director": "John Smith",
        "client": "Acme Corp",
        "department": "IT",
        "kam": "Bob Wilson",
        "business_manager": "Alice Johnson",
        "description": "Test pointage entry"
    }
    response = client.post("/pointages", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "Jane Doe"
    assert data["type_sollicitation"] == "EXPERTISE"
    assert data["practice"] == "Weekly"
    assert data["director"] == "John Smith"
    assert data["client"] == "Acme Corp"
    assert data["department"] == "IT"
    assert data["kam"] == "Bob Wilson"
    assert data["business_manager"] == "Alice Johnson"
    assert data["description"] == "Test pointage entry"
    assert data["start"] is not None
    