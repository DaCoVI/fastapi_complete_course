import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from project_3.TodoApp.core.security import bcrypt_context
from project_3.TodoApp.enum.custom_codes import AuthCode
from project_3.TodoApp.models.users_orm import Users


pytestmark = [pytest.mark.api, pytest.mark.router_auth]

# =====================================================================================
# Endpoint: auth.create_user()
# POST /auth/
# =====================================================================================


@pytest.mark.db
def test_auth_create_user_persists_row(
    client: TestClient,
    db_session: Session,
) -> None:
    payload = {
        "username": "newuser",
        "email": "newuser@example.test",
        "first_name": "New",
        "last_name": "User",
        "password": "ChangeMe123!",
        "phone_number": "123456789",
    }

    response = client.post("/auth/", json=payload)

    assert response.status_code == status.HTTP_201_CREATED

    created = db_session.query(Users).filter(Users.username == "newuser").one()
    assert created.email == payload["email"]
    assert created.first_name == payload["first_name"]
    assert created.last_name == payload["last_name"]
    assert created.is_active is True
    assert created.role in ("user", "UserRole.USER")
    assert bcrypt_context.verify(payload["password"], created.hashed_password) is True


def test_auth_create_user_invalid_payload(client: TestClient) -> None:
    payload = {
        "username": "x",
        "email": "not-an-email",
        "first_name": "New",
        "last_name": "User",
        "password": "short",  # min_length=8
        "phone_number": "123",
    }
    response = client.post("/auth/", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# =====================================================================================
# Endpoint: auth.login_for_access_token()
# POST /auth/token
# =====================================================================================


@pytest.mark.db
def test_auth_token_returns_bearer_token(
    client: TestClient,
    db_session: Session,
) -> None:
    raw_pw = "Correct123!"
    user = Users(
        email="u1@example.test",
        username="u1",
        first_name="U",
        last_name="One",
        hashed_password=bcrypt_context.hash(raw_pw),
        role="user",
        is_active=True,
        phone_number="111111",
    )
    db_session.add(user)
    db_session.flush()
    form = {"username": "u1", "password": raw_pw}

    response = client.post("/auth/token", data=form)
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 10


@pytest.mark.db
def test_auth_token_wrong_password(
    client: TestClient,
    db_session: Session,
) -> None:
    user = Users(
        email="u1@example.test",
        username="u1",
        first_name="U",
        last_name="One",
        hashed_password=bcrypt_context.hash("Correct123!"),
        role="user",
        is_active=True,
        phone_number="111111",
    )
    db_session.add(user)
    db_session.flush()

    response = client.post(
        "/auth/token", data={"username": "u1", "password": "Wrong123!"}
    )
    data = response.json()

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert data["detail"]["code"] == AuthCode.INVALID


def test_auth_token_missing_form_fields(client: TestClient) -> None:
    response = client.post("/auth/token", data={"username": "u1"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
