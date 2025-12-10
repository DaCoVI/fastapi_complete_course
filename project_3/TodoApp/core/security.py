from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, HTTPException
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from starlette import status

from project_3.TodoApp.core.config import ALGORITHM, SECRET_KEY

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_bearer)],
) -> dict[str, str | int]:
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=ALGORITHM)
        username: str | None = payload.get("sub")
        id: int | None = payload.get("id")
        role: str | None = payload.get("role")
        if not username or not id or not role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user.",
            )
        return {"username": username, "id": id, "role": role}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user."
        )


user_dependency = Annotated[dict, Depends(get_current_user)]


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
