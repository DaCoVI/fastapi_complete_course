import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from project_3.TodoApp.enum.custom_codes import AuthCode, TodoCode
from project_3.TodoApp.enum.roles import UserRole
from project_3.TodoApp.models.todos_orm import Todos
from project_3.TodoApp.test.api.conftest import AuthAs
from project_3.TodoApp.test.api.factories import make_todo, make_user


pytestmark = [pytest.mark.api, pytest.mark.router_admin]

# =====================================================================================
# Endpoint: admin.read_all()
# GET /admin/todo
# =====================================================================================


def test_admin_read_all_not_authenticated(client: TestClient, auth_none: None) -> None:
    response = client.get("/admin/todo")
    data = response.json()

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert data["detail"]["code"] == AuthCode.REQUIRED
    assert data["detail"]["message"] == "Authentication required"


def test_admin_read_all_not_authorized(client: TestClient, auth_user: None) -> None:
    response = client.get("/admin/todo")
    data = response.json()

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert data["detail"]["code"] == AuthCode.INVALID
    assert data["detail"]["message"] == "Could not validate user"


@pytest.mark.db
def test_admin_read_all_returns_empty_list(
    client: TestClient, auth_admin: None
) -> None:
    response = client.get("/admin/todo")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


@pytest.mark.db
def test_admin_read_all_returns_all_todos(
    client: TestClient,
    db_session: Session,
    auth_as: AuthAs,
) -> None:
    admin = make_user(db_session, role=UserRole.ADMIN)
    user = make_user(db_session, role=UserRole.USER)

    todo_admin = make_todo(
        db_session,
        owner_id=admin.id,
        title="todo1",
        description="desc1",
        priority=1,
        complete=True,
    )
    todo_user = make_todo(
        db_session,
        owner_id=user.id,
        title="todo2",
        description="desc2",
        priority=5,
        complete=False,
    )

    auth_as(admin.id, admin.role, admin.username)
    response = client.get("/admin/todo")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert data == [
        {
            "title": "todo1",
            "id": todo_admin.id,
            "owner_id": admin.id,
            "description": "desc1",
            "priority": 1,
            "complete": True,
        },
        {
            "title": "todo2",
            "id": todo_user.id,
            "owner_id": user.id,
            "description": "desc2",
            "priority": 5,
            "complete": False,
        },
    ]


# =====================================================================================
# Endpoint: admin.delete_todo()
# DELETE /admin/todo/{todo_id}
# =====================================================================================


def test_admin_delete_not_authenticated(client: TestClient, auth_none: None) -> None:
    response = client.delete("/admin/todo/1")
    data = response.json()

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert data["detail"]["code"] == AuthCode.REQUIRED
    assert data["detail"]["message"] == "Authentication required"


def test_admin_delete_not_authorized(client: TestClient, auth_user: None) -> None:
    response = client.delete("/admin/todo/1")
    data = response.json()

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert data["detail"]["code"] == AuthCode.INVALID
    assert data["detail"]["message"] == "Could not validate user"


def test_admin_delete_invalid_id(client: TestClient, auth_admin: None) -> None:
    response = client.delete("/admin/todo/0")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.db
def test_admin_delete_not_found(
    client: TestClient,
    db_session: Session,
    auth_as: AuthAs,
) -> None:
    admin = make_user(db_session, role=UserRole.ADMIN)
    auth_as(admin.id, admin.role, admin.username)

    response = client.delete("/admin/todo/999")
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data["detail"]["code"] == TodoCode.NOT_FOUND
    assert data["detail"]["message"] == "Todo not found"


@pytest.mark.db
def test_admin_delete_deletes_row(
    client: TestClient,
    db_session: Session,
    auth_as: AuthAs,
) -> None:
    admin = make_user(db_session, role=UserRole.ADMIN)
    user = make_user(db_session, role=UserRole.USER)

    todo_delete = make_todo(
        db_session,
        owner_id=user.id,
        title="delete me",
        description="delete me",
        priority=2,
        complete=False,
    )
    todo_keep = make_todo(
        db_session,
        owner_id=user.id,
        title="keep me",
        description="keep me",
        priority=1,
        complete=True,
    )

    auth_as(admin.id, admin.role, admin.username)

    response = client.delete(f"/admin/todo/{todo_delete.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    deleted = db_session.query(Todos).filter(Todos.id == todo_delete.id).first()
    kept = db_session.query(Todos).filter(Todos.id == todo_keep.id).first()

    assert deleted is None
    assert kept is not None
    assert kept.id == todo_keep.id
    assert kept.title == todo_keep.title
    assert kept.owner_id == user.id
