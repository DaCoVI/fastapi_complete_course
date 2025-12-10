from fastapi import FastAPI
from project_3.TodoApp.database import engine
import project_3.TodoApp.orm_models.users as orm_users
from project_3.TodoApp.routers import admin, auth, todos, users

app = FastAPI()

orm_users.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
