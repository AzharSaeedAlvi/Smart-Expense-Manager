import pytest

from fastapi.testclient import TestClient
from main import app, get_current_user
from models import User



client = TestClient(app)


@pytest.fixture
def as_authenticated_user():
    def _fake_user():
        return User(id =1, name="Test_User", email="test@example.com", hashed_password="x")
    app.dependency_overrides[get_current_user] = _fake_user
    yield
    app.dependency_overrides.clear()
def test_create_expense_rejects_negative_amount(as_authenticated_user):
    response = client.post(
        "/expenses",
        json={"amount": -50, "description": "neg amount", "spent_on": "2026-08-13"},
    )
    assert response.status_code == 422


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status" : "ok"} 


def test_expenses_requires_auth():
    response = client.get("/expenses")
    assert response.status_code == 401



