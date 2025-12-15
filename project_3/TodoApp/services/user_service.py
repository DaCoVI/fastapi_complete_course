from project_3.TodoApp.core.errors.http import AuthInvalid
from project_3.TodoApp.models.users_orm import Users
from sqlalchemy.orm import Session
from project_3.TodoApp.core.security import bcrypt_context


class UserService:
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Users:
        user = db.query(Users).filter(Users.id == user_id).first()
        if not user:
            raise AuthInvalid()
        return user

    @staticmethod
    def authenticate(username: str, password: str, db: Session) -> Users:
        user = db.query(Users).filter(Users.username == username).first()
        if not user:
            raise AuthInvalid()
        if not bcrypt_context.verify(password, user.hashed_password):
            raise AuthInvalid()
        return user

    @staticmethod
    def change_password(db: Session, user_id: int, old: str, new: str) -> None:
        user = UserService.get_user_by_id(db, user_id)
        if not bcrypt_context.verify(old, user.hashed_password):
            raise AuthInvalid()
        user.hashed_password = bcrypt_context.hash(new)
        db.commit()

    @staticmethod
    def change_phone_number(
        db: Session, user_id: int, password: str, new_phone: str
    ) -> None:
        user = UserService.get_user_by_id(db, user_id)
        if not bcrypt_context.verify(password, user.hashed_password):
            raise AuthInvalid()

        user.phone_number = new_phone
        db.commit()
