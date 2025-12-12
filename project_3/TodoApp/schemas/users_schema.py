from pydantic import BaseModel, Field

from project_3.TodoApp.core.config import PASSWORD_MIN_LEN


class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str = Field(min_length=PASSWORD_MIN_LEN)
    phone_number: str | None = None


class UserRead(BaseModel):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
    phone_number: str | None = None


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(min_length=PASSWORD_MIN_LEN)
    new_password: str = Field(min_length=PASSWORD_MIN_LEN)


class ChangePhoneNumberRequest(BaseModel):
    password: str = Field(min_length=PASSWORD_MIN_LEN)
    new_phone_number: str
