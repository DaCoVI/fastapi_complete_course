from fastapi import APIRouter
from project_3.TodoApp.core.security import user_dependency
from project_3.TodoApp.database import db_dependency
from project_3.TodoApp.orm_models.users import Users
from project_3.TodoApp.schemas.users import ChangePasswordRequest, UserRead
from project_3.TodoApp.core.security import bcrypt_context
from fastapi.exceptions import HTTPException
from starlette import status

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/", response_model=UserRead)
async def get_user(user: user_dependency, db: db_dependency) -> Users:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
        )
    result = db.query(Users).filter(Users.id == user.get("id")).first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return result


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    user: user_dependency,
    db: db_dependency,
    payload: ChangePasswordRequest,
) -> None:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
        )

    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")

    if not bcrypt_context.verify(payload.old_password, user_model.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Error on password change",
        )

    user_model.hashed_password = bcrypt_context.hash(payload.new_password)
    db.commit()
