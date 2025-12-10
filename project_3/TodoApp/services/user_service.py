from project_3.TodoApp.orm_models.users import Users
from sqlalchemy.orm import Session
from project_3.TodoApp.core.security import bcrypt_context


def authenticate_user(username: str, password: str, db: Session) -> bool | Users:
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user
