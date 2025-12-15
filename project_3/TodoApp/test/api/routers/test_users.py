import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.orm import Session

from project_3.TodoApp.enum.custom_codes import AuthCode
from project_3.TodoApp.enum.roles import UserRole
from project_3.TodoApp.models.users_orm import Users
from project_3.TodoApp.test.api.conftest import AuthAs
from project_3.TodoApp.test.api.factories import make_user
from project_3.TodoApp.core.security import bcrypt_context

pytestmark = [pytest.mark.api, pytest.mark.router_users]


# =====================================================================================
# Endpoint get_user()
# =====================================================================================


def test_get_user_not_authenticated(client: TestClient, auth_none: None) -> None:
    response = client.get("/user/")
    data = response.json()
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert data["detail"]["code"] == AuthCode.REQUIRED
    assert data["detail"]["message"] == "Authentication required"


@pytest.mark.db
def test_get_user_authenticated(
    client: TestClient, db_session: Session, auth_as: AuthAs
) -> None:
    user = make_user(
        db_session,
        username="Test User 1",
        email="test@mail.com",
        phone_number="123456789",
        first_name="Test",
        last_name="User",
        is_active=True,
        role=UserRole.USER,
    )
    auth_as(user.id, user.role, user.username)
    response = client.get("/user/")
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert data["id"] == user.id
    assert data["username"] == user.username
    assert data["email"] == user.email
    assert data["phone_number"] == user.phone_number
    assert data["first_name"] == user.first_name
    assert data["last_name"] == user.last_name
    assert data["is_active"] == user.is_active
    assert data["role"] == user.role


# =====================================================================================
# Endpoint: change_password()
# =====================================================================================


def test_change_password_not_authenticated(client: TestClient, auth_none: None) -> None:
    response = client.put("/user/password")
    data = response.json()
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert data["detail"]["code"] == AuthCode.REQUIRED
    assert data["detail"]["message"] == "Authentication required"


def test_change_password_invalid_payload(client: TestClient, auth_user: None) -> None:
    payload = {
        "old_password": "short",  # min_length = 8
        "new_password": "short",  # min_length = 8
    }
    response = client.put("/user/password", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.db
def test_change_password_changes_hash(
    client: TestClient,
    db_session: Session,
    auth_as: AuthAs,
) -> None:
    old_pw = "OldPassword123!"
    new_pw = "NewPassword123!"

    user = make_user(
        db_session,
        username="user1",
        email="user1@example.test",
        phone_number="1000",
        password=old_pw,
    )
    auth_as(user.id, user.role, user.username)

    payload = {"old_password": old_pw, "new_password": new_pw}
    response = client.put("/user/password", json=payload)

    assert response.status_code == status.HTTP_204_NO_CONTENT

    refreshed = db_session.query(Users).filter(Users.id == user.id).one()
    assert bcrypt_context.verify(new_pw, refreshed.hashed_password) is True
    assert bcrypt_context.verify(old_pw, refreshed.hashed_password) is False


@pytest.mark.db
def test_change_password_wrong_old_password(
    client: TestClient,
    db_session: Session,
    auth_as: AuthAs,
) -> None:
    user = make_user(
        db_session,
        username="user1",
        email="user1@example.test",
        phone_number="1000",
        password="CorrectOld123!",
    )
    auth_as(user.id, user.role, user.username)

    payload = {"old_password": "WrongOld123!", "new_password": "NewPassword123!"}
    response = client.put("/user/password", json=payload)
    data = response.json()

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert data["detail"]["code"] == AuthCode.INVALID
    assert data["detail"]["message"] == "Could not validate user"


# =====================================================================================
# Endpoint: change_phone_number()
# =====================================================================================


def test_change_phone_not_authenticated(client: TestClient, auth_none: None) -> None:
    response = client.put("/user/phone")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"]["code"] == AuthCode.REQUIRED
    assert response.json()["detail"]["message"] == "Authentication required"


def test_change_phone_invalid_payload(client: TestClient, auth_user: None) -> None:
    payload = {
        "password": "short",  # min_length = 8
        "new_phone_number": "123456789",
    }
    response = client.put("/user/phone", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.db
def test_change_phone_updates_phone_number(
    client: TestClient,
    db_session: Session,
    auth_as: AuthAs,
) -> None:
    pw = "CorrectOld123!"
    user = make_user(
        db_session,
        username="user1",
        email="user1@example.test",
        phone_number="111111",
        password=pw,
    )
    auth_as(user.id, user.role, user.username)

    payload = {"password": pw, "new_phone_number": "222222"}
    response = client.put("/user/phone", json=payload)

    assert response.status_code == status.HTTP_204_NO_CONTENT

    refreshed = db_session.query(Users).filter(Users.id == user.id).one()
    assert refreshed.phone_number == "222222"


@pytest.mark.db
def test_change_phone_wrong_password(
    client: TestClient,
    db_session: Session,
    auth_as: AuthAs,
) -> None:
    user = make_user(
        db_session,
        username="user1",
        email="user1@example.test",
        phone_number="111111",
        password="CorrectOld123!",
    )
    auth_as(user.id, user.role, user.username)

    payload = {"password": "WrongOld123!", "new_phone_number": "222222"}
    response = client.put("/user/phone", json=payload)
    data = response.json()

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert data["detail"]["code"] == AuthCode.INVALID
    assert data["detail"]["message"] == "Could not validate user"
