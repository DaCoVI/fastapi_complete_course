from fastapi.testclient import TestClient
from sqlalchemy import Connection, NestedTransaction, RootTransaction, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm.session import SessionTransaction
from typing import Callable, Generator
import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.pool import StaticPool

from project_3.TodoApp.database import Base

from project_3.TodoApp.database import get_db
from project_3.TodoApp.core.security import JwtUserClaims, get_current_user
from project_3.TodoApp.enum.roles import UserRole
from project_3.TodoApp.main import app

DATABASE_URL = "sqlite+pysqlite:///:memory:"
AuthAs = Callable[[int, UserRole | str, str], None]


@pytest.fixture(scope="session")
def engine() -> Engine:
    engine = create_engine(
        url=DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture()
def db_session(engine: Engine) -> Generator[Session, None, None]:
    connection: Connection = engine.connect()
    transaction: RootTransaction = connection.begin()

    SessionLocal = sessionmaker(bind=connection, autoflush=False, autocommit=False)
    session: Session = SessionLocal()
    nested: NestedTransaction = connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(sess: Session, trans: SessionTransaction) -> None:
        nonlocal nested
        if nested.is_active is False:
            nested = connection.begin_nested()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    try:
        yield test_client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture()
def auth_none() -> Generator[None, None, None]:
    app.dependency_overrides.pop(get_current_user, None)
    yield
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture()
def auth_user() -> Generator[None, None, None]:
    def override() -> JwtUserClaims:
        return {"username": "testuser", "id": 1, "role": UserRole.USER}

    app.dependency_overrides[get_current_user] = override
    yield
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture()
def auth_admin() -> Generator[None, None, None]:
    def override() -> JwtUserClaims:
        return {"username": "admin", "id": 99, "role": UserRole.ADMIN}

    app.dependency_overrides[get_current_user] = override
    yield
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def auth_as() -> Generator[AuthAs, None, None]:
    def auth(
        user_id: int,
        role: UserRole | str = UserRole.USER,
        username: str = "testuser",
    ) -> None:
        def override() -> JwtUserClaims:
            return {"username": username, "id": user_id, "role": role}

        app.dependency_overrides[get_current_user] = override

    yield auth

    app.dependency_overrides.pop(get_current_user, None)
