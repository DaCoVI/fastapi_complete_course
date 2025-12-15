from fastapi import APIRouter, Path
from fastapi import status
from project_3.TodoApp.core.errors.http import AuthInvalid, AuthRequired, TodoNotFound
from project_3.TodoApp.enum.roles import UserRole
from project_3.TodoApp.models.todos_orm import Todos
from project_3.TodoApp.core.security import user_dependency
from project_3.TodoApp.database import db_dependency
from project_3.TodoApp.schemas.todos_schema import TodoRead

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)


@router.get(
    "/todo",
    status_code=status.HTTP_200_OK,
    response_model=list[TodoRead],
)
async def read_all(user: user_dependency, db: db_dependency) -> list[Todos]:
    if user is None:
        raise AuthRequired()
    if user.get("role") != UserRole.ADMIN:
        raise AuthInvalid()
    return db.query(Todos).all()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user: user_dependency,
    db: db_dependency,
    todo_id: int = Path(gt=0),
) -> None:
    if user is None:
        raise AuthRequired()
    if user.get("role") != UserRole.ADMIN:
        raise AuthInvalid()
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise TodoNotFound()
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()
