from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from project_3.TodoApp.core.errors.http import AuthInvalid, AuthRequired
import project_3.TodoApp.core.security as security
import project_3.TodoApp.core.config as config
from project_3.TodoApp.test.unit.conftest import decode_verify


pytestmark = pytest.mark.unit


def test_create_access_token_contains_expected_claims_and_exp(
    fixed_jwt_settings: None,
) -> None:
    now = datetime.now(timezone.utc)
    token = security.create_access_token(
        username="alice",
        user_id=123,
        role="user",
        expires_delta=timedelta(minutes=15),
    )

    payload = decode_verify(token)

    assert payload["sub"] == "alice"
    assert payload["id"] == 123
    assert payload["role"] == "user"

    exp_dt = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)

    assert now < exp_dt <= now + timedelta(minutes=15, seconds=5)


@pytest.mark.anyio
async def test_get_current_user_raises_required_when_token_is_none(
    fixed_jwt_settings: None,
) -> None:
    with pytest.raises(AuthRequired):
        await security.get_current_user(token=None)


@pytest.mark.anyio
async def test_get_current_user_raises_invalid_on_garbage_token(
    fixed_jwt_settings: None,
) -> None:
    with pytest.raises(AuthInvalid):
        await security.get_current_user(token="not-a-jwt")


@pytest.mark.anyio
async def test_get_current_user_raises_invalid_when_signature_key_is_wrong(
    fixed_jwt_settings: None,
) -> None:
    other_token = jwt.encode(
        claims={
            "sub": "alice",
            "id": 1,
            "role": "user",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        },
        key="different-key",
        algorithm=config.ALGORITHM,
    )

    with pytest.raises(AuthInvalid):
        await security.get_current_user(token=other_token)


@pytest.mark.anyio
async def test_get_current_user_raises_invalid_when_claim_missing(
    fixed_jwt_settings: None,
) -> None:
    token_missing_role = jwt.encode(
        claims={
            "sub": "alice",
            "id": 1,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        },
        key=config.SECRET_KEY,
        algorithm=config.ALGORITHM,
    )

    with pytest.raises(AuthInvalid):
        await security.get_current_user(token=token_missing_role)


@pytest.mark.anyio
async def test_get_current_user_raises_invalid_when_token_expired(
    fixed_jwt_settings: None,
) -> None:
    expired = security.create_access_token(
        username="alice",
        user_id=1,
        role="user",
        expires_delta=timedelta(seconds=-1),
    )

    with pytest.raises(AuthInvalid):
        await security.get_current_user(token=expired)


@pytest.mark.anyio
async def test_get_current_user_returns_claims_on_success(
    fixed_jwt_settings: None,
) -> None:
    token = security.create_access_token(
        username="alice",
        user_id=123,
        role="admin",
        expires_delta=timedelta(minutes=5),
    )

    claims = await security.get_current_user(token=token)

    assert claims == {"username": "alice", "id": 123, "role": "admin"}
