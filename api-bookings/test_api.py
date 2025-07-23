import requests
import os, dotenv

dotenv.load_dotenv()
API_KEY = os.getenv("API_KEY")
HEADERS = {"x-api-key": API_KEY}

def test_get_pointages():
    response = requests.get("https://pointages.onrender.com/pointages", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Optionally, check for expected keys in the first record
    if data:
        record = data[0]
        assert "name" in record
        assert "type_sollicitation" in record

def test_post_pointage():
    payload = {
        "name": "Test User",
        "type_sollicitation": "EXPERTISE",
        "practice": "Weekly",
        "director": "John Smith",
        "client": "Acme Corp",
        "department": "IT",
        "kam": "Bob Wilson",
        "business_manager": "Alice Johnson",
        "description": "Test entry from pytest"
    }
    response = requests.post("https://pointages.onrender.com/pointages", json=payload, headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test User"
    assert data["type_sollicitation"] == "EXPERTISE"