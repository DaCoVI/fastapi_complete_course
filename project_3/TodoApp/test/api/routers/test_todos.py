from fastapi import status
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session

from project_3.TodoApp.enum.custom_codes import AuthCode, TodoCode
from project_3.TodoApp.models.todos_orm import Todos
from project_3.TodoApp.test.api.conftest import AuthAs
from project_3.TodoApp.test.api.factories import make_todo, make_user


pytestmark = pytest.mark.api

# =====================================================================================
# Endpoint: read_all()
# =====================================================================================


def test_read_all_not_authenticated(client: TestClient, auth_none: None) -> None:
    response = client.get("/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"]["code"] == AuthCode.REQUIRED
    assert response.json()["detail"]["message"] == "Authentication required"


def test_read_all_returns_empty_list_when_no_todos(
    client: TestClient, auth_user: None
) -> None:
    response = client.get("/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


@pytest.mark.db
def test_read_all_returns_two_todos(
    client: TestClient,
    db_session: Session,
    auth_as: AuthAs,
) -> None:
    user = make_user(db_session)
    todo1 = make_todo(
        db_session,
        owner_id=user.id,
        title="todo1",
        description="desc1",
        priority=1,
        complete=True,
    )
    todo2 = make_todo(
        db_session,
        owner_id=user.id,
        title="todo2",
        description="desc2",
        priority=5,
        complete=False,
    )
    auth_as(user.id, user.role, user.username)
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2
    assert response.json() == [
        {
            "title": "todo1",
            "id": todo1.id,
            "owner_id": user.id,
            "description": "desc1",
            "priority": 1,
            "complete": True,
        },
        {
            "title": "todo2",
            "id": todo2.id,
            "owner_id": user.id,
            "description": "desc2",
            "priority": 5,
            "complete": False,
        },
    ]


@pytest.mark.db
def test_read_all_returns_user_specific_todos_only(
    client: TestClient,
    db_session: Session,
    auth_as: AuthAs,
) -> None:
    user1 = make_user(db_session)
    user2 = make_user(db_session)
    make_todo(
        db_session,
        owner_id=user1.id,
        title="todo 1",
        description="description 1",
        priority=1,
        complete=False,
    )
    make_todo(
        db_session,
        owner_id=user2.id,
        title="todo 2",
        description="description 2",
        priority=2,
        complete=False,
    )

    auth_as(user1.id, user1.role, user1.username)
    response = client.get("/")
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 1
    assert data[0]["owner_id"] == user1.id
    assert data[0]["title"] == "todo 1"
    assert data[0]["description"] == "description 1"
    assert data[0]["priority"] == 1
    assert data[0]["complete"] is False
    assert data[0]["owner_id"] == user1.id


# =====================================================================================
# Endpoint: read_todo()
# =====================================================================================


def test_read_todo_with_no_todos(client: TestClient, auth_user: None) -> None:
    response = client.get("/todo/1")
    data = response.json()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data["detail"]["code"] == TodoCode.NOT_FOUND
    assert data["detail"]["message"] == "Todo not found"


def test_read_todo_invalid_id(client: TestClient, auth_user: None) -> None:
    response = client.get("/todo/0")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_read_todo_not_authenticated(client: TestClient, auth_none: None) -> None:
    response = client.get("/todo/1")
    data = response.json()
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert data["detail"]["code"] == AuthCode.REQUIRED
    assert data["detail"]["message"] == "Authentication required"


@pytest.mark.db
def test_read_todo_with_one_todo(
    client: TestClient,
    db_session: Session,
    auth_as: AuthAs,
) -> None:
    user = make_user(db_session)
    todo = make_todo(
        db_session,
        owner_id=user.id,
        title="todo 1",
        description="description 1",
        priority=1,
        complete=False,
    )
    auth_as(user.id, user.role, user.username)
    response = client.get(f"/todo/{todo.id}")
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data["owner_id"] == user.id
    assert data["title"] == "todo 1"
    assert data["description"] == "description 1"
    assert data["priority"] == 1
    assert data["complete"] is False
    assert data["owner_id"] == user.id


@pytest.mark.db
def test_read_todo_with_one_todo_but_wrong_user(
    client: TestClient,
    db_session: Session,
    auth_as: AuthAs,
) -> None:
    user1 = make_user(db_session)
    user2 = make_user(db_session)
    todo = make_todo(
        db_session,
        owner_id=user2.id,
        title="todo 1",
        description="description 1",
        priority=1,
        complete=False,
    )
    auth_as(user1.id, user1.role, user1.username)
    response = client.get(f"/todo/{todo.id}")
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data["detail"]["code"] == TodoCode.NOT_FOUND
    assert data["detail"]["message"] == "Todo not found"


# =====================================================================================
# Endpoint: create_todo()
# =====================================================================================


def test_create_todo_not_authorized(client: TestClient, auth_none: None) -> None:
    response = client.post("/todo")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"]["code"] == AuthCode.REQUIRED
    assert response.json()["detail"]["message"] == "Authentication required"


@pytest.mark.db
def test_create_todo_persists_row(
    client: TestClient,
    db_session: Session,
    auth_as: AuthAs,
) -> None:
    user = make_user(db_session)
    auth_as(user.id, user.role, user.username)

    payload = {
        "title": "title1",
        "description": "description1",
        "priority": 3,
        "complete": False,
    }

    response = client.post("/todo", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    rows = db_session.query(Todos).filter(Todos.owner_id == user.id).all()
    assert len(rows) == 1

    created = rows[0]
    assert created.title == payload["title"]
    assert created.description == payload["description"]
    assert created.priority == payload["priority"]
    assert created.complete == payload["complete"]
    assert created.owner_id == user.id
    assert created.id == 1


def test_create_todo_invalid_payload(
    client: TestClient,
    auth_user: None,
) -> None:
    payload = {
        "title": "x",  # min_lenght = 3
        "description": "y",  # min_lenght = 3
        "priority": 99,  # lt=6, gt=0
        "complete": None,  # wrong type
    }
    response = client.post("/todo", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# =====================================================================================
# Endpoint: update_todo()
# =====================================================================================


def test_update_todo_not_authorized(client: TestClient, auth_none: None) -> None:
    response = client.put("/todo/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"]["code"] == AuthCode.REQUIRED
    assert response.json()["detail"]["message"] == "Authentication required"


def test_update_todo_invalid_id(client: TestClient, auth_user: None) -> None:
    response = client.put("/todo/0")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.db
def test_update_todo_not_found(
    client: TestClient, db_session: Session, auth_as: AuthAs
) -> None:
    user = make_user(db_session)
    auth_as(user.id, user.role, user.username)
    make_todo(db_session, owner_id=user.id)

    payload = {
        "title": "todo title",
        "description": "todo description",
        "priority": 4,
        "complete": True,
    }

    response = client.put("/todo/99", json=payload)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"]["code"] == TodoCode.NOT_FOUND


@pytest.mark.db
def test_update_todo_user_specific(
    client: TestClient, db_session: Session, auth_as: AuthAs
) -> None:
    user1 = make_user(db_session)
    user2 = make_user(db_session)
    auth_as(user1.id, user1.role, user1.username)
    todo = make_todo(
        db_session,
        owner_id=user2.id,
        title="original",
        description="original",
        priority=1,
        complete=False,
    )

    payload = {
        "title": "todo title",
        "description": "todo description",
        "priority": 4,
        "complete": True,
    }

    response = client.put(f"/todo/{todo.id}", json=payload)
    unchanged = db_session.query(Todos).filter(Todos.id == todo.id).one()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"]["code"] == TodoCode.NOT_FOUND
    assert unchanged.title == todo.title
    assert unchanged.description == todo.description
    assert unchanged.complete == todo.complete
    assert unchanged.priority == todo.priority
    assert unchanged.owner_id == todo.owner_id


@pytest.mark.db
def test_update_todo_changed(
    client: TestClient, db_session: Session, auth_as: AuthAs
) -> None:
    user = make_user(db_session)
    auth_as(user.id, user.role, user.username)
    todo = make_todo(
        db_session,
        owner_id=user.id,
        title="my title",
        description="my description",
        priority=1,
        complete=False,
    )

    payload = {
        "title": "todo title",
        "description": "todo description",
        "priority": 4,
        "complete": True,
    }

    response = client.put(f"/todo/{todo.id}", json=payload)
    rows = db_session.query(Todos).filter(Todos.owner_id == user.id).all()
    updated = rows[0]

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert updated.complete is True
    assert updated.description == payload["description"]
    assert updated.title == payload["title"]
    assert updated.priority == payload["priority"]


# =====================================================================================
# Endpoint: delete_todo()
# =====================================================================================


def test_delete_todo_not_authorized(client: TestClient, auth_none: None) -> None:
    response = client.delete("/todo/1")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"]["code"] == AuthCode.REQUIRED
    assert response.json()["detail"]["message"] == "Authentication required"


@pytest.mark.db
def test_delete_todo_not_found(
    client: TestClient,
    db_session: Session,
    auth_as: AuthAs,
) -> None:
    user = make_user(db_session)
    auth_as(user.id, user.role, user.username)

    response = client.delete("/todo/99")
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data["detail"]["code"] == TodoCode.NOT_FOUND
    assert data["detail"]["message"] == "Todo not found"


@pytest.mark.db
def test_delete_todo_user_specific(
    client: TestClient,
    db_session: Session,
    auth_as: AuthAs,
) -> None:
    user1 = make_user(db_session)
    user2 = make_user(db_session)

    todo = make_todo(
        db_session,
        owner_id=user2.id,
        title="foreign",
        description="foreign",
        priority=1,
        complete=False,
    )

    auth_as(user1.id, user1.role, user1.username)

    response = client.delete(f"/todo/{todo.id}")
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data["detail"]["code"] == TodoCode.NOT_FOUND
    assert data["detail"]["message"] == "Todo not found"

    # DB unveraendert
    still_there = db_session.query(Todos).filter(Todos.id == todo.id).one()
    assert still_there.owner_id == user2.id
    assert still_there.title == "foreign"
    assert still_there.description == "foreign"
    assert still_there.priority == 1
    assert still_there.complete is False


@pytest.mark.db
def test_delete_todo_deletes_correct_row(
    client: TestClient,
    db_session: Session,
    auth_as: AuthAs,
) -> None:
    user = make_user(db_session)
    todo = make_todo(
        db_session,
        owner_id=user.id,
        title="to delete",
        description="to delete",
        priority=2,
        complete=False,
    )
    todo_keep = make_todo(
        db_session,
        owner_id=user.id,
        title="do not delete",
        description="do not delete",
        priority=1,
        complete=True,
    )

    auth_as(user.id, user.role, user.username)

    response = client.delete(f"/todo/{todo.id}")
    deleted = db_session.query(Todos).filter(Todos.id == todo.id).first()
    still_there = db_session.query(Todos).filter(Todos.id == todo_keep.id).first()
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert deleted is None
    assert still_there is not None
    assert still_there.complete is True
    assert still_there.description == todo_keep.description
    assert still_there.id == todo_keep.id
    assert still_there.owner_id == user.id
    assert still_there.priority == todo_keep.priority
    assert still_there.title == todo_keep.title
