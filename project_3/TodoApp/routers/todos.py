from fastapi import APIRouter, Path
from project_3.TodoApp.core.errors.http import TodoNotFound
from project_3.TodoApp.schemas import todos_schema
from project_3.TodoApp.models.todos_orm import Todos
from project_3.TodoApp.database import db_dependency
from project_3.TodoApp.core.security import user_dependency


router = APIRouter(tags=["todo"])


@router.get("/", response_model=list[todos_schema.TodoRead], status_code=200)
async def read_all(user: user_dependency, db: db_dependency) -> list[Todos]:
    return db.query(Todos).filter(Todos.owner_id == user.get("id")).all()


@router.get("/todo/{todo_id}", response_model=todos_schema.TodoRead, status_code=200)
async def read_todo(
    user: user_dependency,
    db: db_dependency,
    todo_id: int = Path(gt=0),
) -> Todos:
    todo_model = (
        db.query(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get("id"))
        .first()
    )
    if todo_model:
        return todo_model
    raise TodoNotFound()


@router.post("/todo", status_code=201)
async def create_todo(
    user: user_dependency,
    db: db_dependency,
    todo_request: todos_schema.TodoRequest,
) -> None:
    todo_model = Todos(**todo_request.model_dump(), owner_id=user.get("id"))
    db.add(todo_model)
    db.commit()


@router.put("/todo/{todo_id}", status_code=204)
async def update_todo(
    user: user_dependency,
    db: db_dependency,
    todo_request: todos_schema.TodoRequest,
    todo_id: int = Path(gt=0),
) -> None:
    todo = (
        db.query(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get("id"))
        .first()
    )
    if not todo:
        raise TodoNotFound()
    todo.title = todo_request.title
    todo.description = todo_request.description
    todo.priority = todo_request.priority
    todo.complete = todo_request.complete
    db.add(todo)
    db.commit()


@router.delete("/todo/{todo_id}", status_code=204)
async def delete_todo(
    user: user_dependency,
    db: db_dependency,
    todo_id: int = Path(gt=0),
) -> None:
    todo = (
        db.query(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get("id"))
        .first()
    )
    if not todo:
        raise TodoNotFound()
    db.query(Todos).filter(Todos.id == todo_id).filter(
        Todos.owner_id == user.get("id")
    ).delete()
    db.commit()
