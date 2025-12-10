from pydantic import BaseModel, Field


class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str = Field(min_length=8)


class UserRead(BaseModel):
    id: int | None
    username: str
    email: str
    first_name: str
    last_name: str
    role: str
    is_active: bool


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(min_length=8)
    new_password: str = Field(min_length=8)
