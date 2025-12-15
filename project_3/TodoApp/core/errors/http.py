from fastapi import HTTPException, status

from project_3.TodoApp.enum.custom_codes import AuthCode, TodoCode


class AuthRequired(HTTPException):
    def __init__(self, *, message: str = "Authentication required") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": AuthCode.REQUIRED, "message": message},
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthInvalid(HTTPException):
    def __init__(self, *, message: str = "Could not validate user") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": AuthCode.INVALID, "message": message},
            headers={"WWW-Authenticate": "Bearer"},
        )


class TodoNotFound(HTTPException):
    def __init__(self, *, message: str = "Todo not found") -> None:
        super().__init__(
            status.HTTP_404_NOT_FOUND,
            {"code": TodoCode.NOT_FOUND, "message": message},
        )
