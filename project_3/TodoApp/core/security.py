from datetime import datetime, timedelta, timezone
from typing import Annotated, TypedDict
from fastapi import Depends
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer


from project_3.TodoApp.core.config import ALGORITHM, SECRET_KEY
from project_3.TodoApp.core.errors.http import AuthInvalid, AuthRequired
from project_3.TodoApp.enum.roles import UserRole

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)


class JwtUserClaims(TypedDict):
    username: str
    id: int
    role: UserRole | str


async def get_current_user(
    token: Annotated[str | None, Depends(oauth2_bearer)],
) -> JwtUserClaims:
    try:
        if token is None:
            raise AuthRequired()
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=ALGORITHM)
        username: str | None = payload.get("sub")
        id: int | None = payload.get("id")
        role: UserRole | None = payload.get("role")
        if not username or not id or not role:
            raise AuthInvalid()
        return {"username": username, "id": id, "role": role}
    except JWTError:
        raise AuthInvalid()


user_dependency = Annotated[JwtUserClaims, Depends(get_current_user)]


def create_access_token(
    username: str,
    user_id: int,
    role: str,
    expires_delta: timedelta,
) -> str:
    encode: dict[str, str | datetime | int] = {
        "sub": username,
        "id": user_id,
        "role": role,
    }
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(claims=encode, key=SECRET_KEY, algorithm=ALGORITHM)
