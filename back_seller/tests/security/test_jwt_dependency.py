from uuid import uuid4

import pytest
from fastapi import HTTPException
from jose import jwt

from app.config import ALGORITHM, SECRET_KEY
from app.security.jwt_dependency import get_current_user


class MockCredentials:
    def __init__(self, token: str):
        self.credentials = token


@pytest.mark.asyncio
async def test_get_current_user_success():
    user_id = str(uuid4())
    token = jwt.encode({"sub": user_id}, SECRET_KEY, algorithm=ALGORITHM)
    credentials = MockCredentials(token)
    result = await get_current_user(credentials)
    assert str(result["userId"]) == user_id


@pytest.mark.asyncio
async def test_get_current_user_no_sub():
    token = jwt.encode({}, SECRET_KEY, algorithm=ALGORITHM)
    credentials = MockCredentials(token)
    with pytest.raises(HTTPException) as exc:
        await get_current_user(credentials)
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_invalid_uuid():
    token = jwt.encode({"sub": "not-a-uuid"}, SECRET_KEY, algorithm=ALGORITHM)
    credentials = MockCredentials(token)
    with pytest.raises(HTTPException) as exc:
        await get_current_user(credentials)
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    credentials = MockCredentials("broken.token.value")
    with pytest.raises(HTTPException) as exc:
        await get_current_user(credentials)
    assert exc.value.status_code == 401
