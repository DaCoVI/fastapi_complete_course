from dataclasses import dataclass
from uuid import uuid4
from sqlalchemy.orm import Session

from project_3.TodoApp.enum.roles import UserRole
from project_3.TodoApp.models.todos_orm import Todos
from project_3.TodoApp.models.users_orm import Users
from project_3.TodoApp.core.security import bcrypt_context


def _unique(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex}"


@dataclass(slots=True)
class UserDefaults:
    password: str = "ChangeMe123!"
    first_name: str = "Test"
    last_name: str = "User"
    is_active: bool = True


@dataclass(slots=True)
class TodoDefaults:
    title: str = "Learn to code!"
    description: str = "Need to learn everyday!"
    priority: int = 1
    complete: bool = False


def make_user(
    db: Session,
    *,
    username: str | None = None,
    email: str | None = None,
    phone_number: str | None = None,
    password: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
    is_active: bool | None = None,
    role: UserRole = UserRole.USER,
    persist: bool = False,
) -> Users:
    defaults = UserDefaults()
    raw_pw = password or defaults.password

    user = Users(
        username=username or _unique("user"),
        email=email or f"{_unique('mail')}@example.test",
        phone_number=phone_number or _unique("tel"),
        first_name=first_name or defaults.first_name,
        last_name=last_name or defaults.last_name,
        hashed_password=bcrypt_context.hash(raw_pw),
        role=role.value,
        is_active=defaults.is_active if is_active is None else is_active,
    )
    db.add(user)
    db.flush()

    return user


def seed_users(
    db: Session,
    *,
    n: int,
    persist: bool = False,
) -> list[Users]:
    if n < 0:
        raise ValueError("n must be >= 0")

    users = [make_user(db) for _ in range(n)]
    return users


def make_todo(
    db: Session,
    *,
    owner_id: int,
    title: str | None = None,
    description: str | None = None,
    priority: int | None = None,
    complete: bool | None = None,
) -> Todos:
    defaults = TodoDefaults()
    auto_title = _unique(defaults.title)

    todo = Todos(
        owner_id=owner_id,
        title=title or auto_title,
        description=description or defaults.description,
        priority=defaults.priority if priority is None else priority,
        complete=defaults.complete if complete is None else complete,
    )
    db.add(todo)
    db.flush()

    return todo


def seed_todos(
    db: Session, *, n: int, owner_id: int, persist: bool = False
) -> list[Todos]:
    if n < 0:
        raise ValueError("n must be >= 0")

    todos = [make_todo(db, owner_id=owner_id) for _ in range(n)]
    db.flush()

    return todos
