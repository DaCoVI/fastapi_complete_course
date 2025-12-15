from fastapi import APIRouter
from project_3.TodoApp.core.security import user_dependency
from project_3.TodoApp.database import db_dependency
from project_3.TodoApp.models.users_orm import Users
from project_3.TodoApp.schemas.users_schema import (
    ChangePasswordRequest,
    ChangePhoneNumberRequest,
    UserRead,
)
from fastapi import status

from project_3.TodoApp.services.user_service import UserService

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/", response_model=UserRead, status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency) -> Users:
    return UserService.get_user_by_id(db, user["id"])


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    user: user_dependency,
    db: db_dependency,
    payload: ChangePasswordRequest,
) -> None:
    UserService.change_password(
        db,
        user["id"],
        payload.old_password,
        payload.new_password,
    )


@router.put("/phone", status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number(
    user: user_dependency,
    db: db_dependency,
    payload: ChangePhoneNumberRequest,
) -> None:
    UserService.change_phone_number(
        db,
        user["id"],
        payload.password,
        payload.new_phone_number,
    )
