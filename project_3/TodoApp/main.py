from typing import Annotated, Generator
from fastapi import Depends, FastAPI, HTTPException, Path
from project_3.TodoApp import schemas
from project_3.TodoApp.database import SessionLocal, engine
import project_3.TodoApp.models as models
from sqlalchemy.orm import Session


app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DbDependency = Annotated[Session, Depends(get_db)]


@app.get("/", response_model=list[schemas.TodoRead], status_code=200)
async def read_all(db: DbDependency) -> list[models.Todos]:
    return db.query(models.Todos).all()


@app.get("/todo/{todo_id}", response_model=schemas.TodoRead, status_code=200)
async def read_todo(
    db: Annotated[Session, Depends(get_db)], todo_id: int = Path(gt=0)
) -> models.Todos:
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if todo_model:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found")


@app.post("/todo", status_code=201)
async def create_todo(
    db: Annotated[Session, Depends(get_db)],
    todo_request: schemas.TodoRequest,
) -> None:
    todo_model = models.Todos(**todo_request.model_dump())
    db.add(todo_model)
    db.commit()


@app.put("/todo/{todo_id}", status_code=204)
async def update_todo(
    db: Annotated[Session, Depends(get_db)],
    todo_request: schemas.TodoRequest,
    todo_id: int = Path(gt=0),
) -> None:
    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo.title = todo_request.title
    todo.description = todo_request.description
    todo.priority = todo_request.priority
    todo.complete = todo_request.complete
    db.add(todo)
    db.commit()


@app.delete("/todo/{todo_id}", status_code=204)
async def delete_todo(
    db: Annotated[Session, Depends(get_db)], todo_id: int = Path(gt=0)
) -> None:
    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()
    db.commit()
