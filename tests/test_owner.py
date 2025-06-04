import pytest
from app import app, db
from models import Owner

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_create_owner(client):
    response = client.post("/owners", json={
        "email": "test@example.com",
        "password": "pass123"
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data["email"] == "test@example.com"

def test_get_owner(client):
    client.post("/owners", json={"email": "test@example.com", "password": "pass123"})
    response = client.get("/owners/1")
    assert response.status_code == 200
    assert response.get_json()["email"] == "test@example.com"
