import pytest

from fastapi.testclient import TestClient
from main import app, get_current_user
from models import User

from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import get_db
from models import Base, Expense



client = TestClient(app)

@pytest.fixture
def test_db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def _override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db

    seed = TestingSessionLocal()
    try:
        yield seed
    finally:
            seed.close()
            app.dependency_overrides.clear()
            Base.metadata.drop_all(bind=engine)

def test_cross_user_isolation(test_db):
    user1 = User(name="User One", email="u1@test.com", hashed_password="x")
    user2 = User(name="User Two", email="u2@test.com", hashed_password="x")
    test_db.add_all([user1, user2])
    test_db.commit()
    u1_id, u2_id = user1.id, user2.id

    expense = Expense(
        amount=42,
        description="user2 private expense",
        spent_on=date(2026, 8, 13),
        user_id=u2_id,
    )
    test_db.add(expense)
    test_db.commit()
    expense_id = expense.id

    #Impersonating the owner -> should see it
    app.dependency_overrides[get_current_user] = lambda: User(id=u2_id)
    owner = client.get(f"/expenses/{expense_id}")
    assert owner.status_code == 200

    #Impersonating a different user -> must NOT see it
    app.dependency_overrides[get_current_user] = lambda: User(id=u1_id)
    other = client.get(f"/expenses/{expense_id}")
    assert other.status_code == 404


def test_list_expenses_respects_limit(test_db):
    user = User(name="Pager", email="pager@test.com", hashed_password="x")
    test_db.add(user)
    test_db.commit()
    uid = user.id

    for i in range(5):
        test_db.add(Expense(
            amount=10 + i,
            description=f"expense {i}",
            spent_on=date(2026, 8, 13),
            user_id=uid,
        ))
    test_db.commit()

    app.dependency_overrides[get_current_user] = lambda: User(id=uid)

    capped = client.get("/expenses?limit=2")
    assert capped.status_code == 200
    assert len(capped.json()) == 2

    over_cap = client.get("/expenses?limit=999")
    assert over_cap.status_code == 422


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



