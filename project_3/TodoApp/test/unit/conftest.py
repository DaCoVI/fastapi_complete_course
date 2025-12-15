from typing import Any
import pytest
from jose import jwt
from project_3.TodoApp.core import config, security


@pytest.fixture()
def fixed_jwt_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(config, "SECRET_KEY", "test-secret-key")
    monkeypatch.setattr(config, "ALGORITHM", "HS256")
    monkeypatch.setattr(security, "SECRET_KEY", "test-secret-key")
    monkeypatch.setattr(security, "ALGORITHM", "HS256")


def decode_no_verify_exp(token: str) -> dict[str, Any]:
    return jwt.decode(
        token,
        key=config.SECRET_KEY,
        algorithms=[config.ALGORITHM],
        options={"verify_exp": False},
    )


def decode_verify(token: str) -> dict[str, Any]:
    return jwt.decode(
        token,
        key=config.SECRET_KEY,
        algorithms=[config.ALGORITHM],
        options={"verify_exp": True},
    )
