from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from project_3.TodoApp.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from project_3.TodoApp.enum.roles import UserRole
from project_3.TodoApp.orm_models.users import Users
from project_3.TodoApp.schemas.token import Token
from project_3.TodoApp.schemas.users import CreateUserRequest
from project_3.TodoApp.database import db_dependency
from project_3.TodoApp.core.security import bcrypt_context, create_access_token
from project_3.TodoApp.services.user_service import authenticate_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    db: db_dependency,
    create_user_request: CreateUserRequest,
) -> None:
    create_user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=UserRole.USER,
        is_active=True,
        hashed_password=bcrypt_context.hash(create_user_request.password),
    )
    db.add(create_user_model)
    db.commit()


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: db_dependency,
) -> Token | str:
    user = authenticate_user(form_data.username, form_data.password, db)
    if not isinstance(user, Users):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user."
        )
    token = create_access_token(
        username=user.username,
        user_id=user.id,
        role=user.role,
        expires_delta=ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    return Token(access_token=token, token_type="bearer")
