import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import asyncio
import uuid

import pytest
from httpx import AsyncClient
from jose import jwt
from sqlalchemy import Enum as SAEnum
from sqlalchemy import String
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

import app.models as models_module


def patch_enum_classes():
    for name in dir(models_module):
        attr = getattr(models_module, name)
        if hasattr(attr, "__table__"):
            table = attr.__table__
            for column in table.columns:
                if isinstance(column.type, SAEnum):
                    column.type = String()
patch_enum_classes()

import app.database.session as session_module
from app.database.base import Base
from app.database.session import get_db
from app.main import app
from app.security.jwt_dependency import ALGORITHM, SECRET_KEY

TEST_DB = "sqlite+aiosqlite://"

@pytest.fixture(scope="session", autouse=True)
def patch_engine():
    engine = create_async_engine(TEST_DB, future=True)

    session_module.engine = engine
    session_module.async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    return engine

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop

@pytest.fixture
async def test_db(patch_engine):
    engine = patch_engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    TestSession = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    yield TestSession
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def client(test_db):

    async def override_db():
        async with test_db() as session:
            yield session

    app.dependency_overrides[get_db] = override_db

    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c

@pytest.fixture
def seller_token():
    return jwt.encode(
        {"userId": str(uuid.uuid4()), "isSeller": True},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

@pytest.fixture
def non_seller_token():
    return jwt.encode(
        {"userId": str(uuid.uuid4()), "isSeller": False},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

@pytest.fixture
def bad_token():
    return "invalid.token"