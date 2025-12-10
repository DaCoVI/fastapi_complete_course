from fastapi import APIRouter, HTTPException, Path
from starlette import status
from project_3.TodoApp.enum.roles import UserRole
from project_3.TodoApp.orm_models.todos import Todos
from project_3.TodoApp.core.security import user_dependency
from project_3.TodoApp.database import db_dependency
from project_3.TodoApp.schemas.todo import TodoRead

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
    if user is None or user.get("role") != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
        )
    return db.query(Todos).all()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user: user_dependency,
    db: db_dependency,
    todo_id: int = Path(gt=0),
) -> None:
    if user is None or user.get("role") != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
        )
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()
