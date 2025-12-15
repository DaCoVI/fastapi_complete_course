from enum import Enum


class AuthCode(str, Enum):
    """
    Machine-readable authentication codes used i.e. in HTTP 401
    (Unauthorized) responses.

    These codes are intended for clients and tests to reliably identify the
    type without depending on human-readable message text.

    Example response payload shape:
    ```
    {
        "detail": {
            "code": "AUTH_REQUIRED",
            "message": "Authentication required"
        }
    }
    ```
    """

    REQUIRED = "AUTH_REQUIRED"
    INVALID = "AUTH_INVALID"


class TodoCode(str, Enum):
    NOT_FOUND = "TODO_NOT_FOUND"
