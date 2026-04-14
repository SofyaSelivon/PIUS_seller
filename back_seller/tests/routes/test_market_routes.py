from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from app.routes.market_routes import create_market_route, my_market, update_my_market
from app.schemas.market_schema import MarketCreate, MarketUpdate


@pytest.fixture
def db():
    return AsyncMock()


@pytest.fixture
def user():
    return {"userId": "test-user"}


@pytest.mark.asyncio
async def test_create_market_success(db, user):
    data = MarketCreate(marketName="Test Market")
    with (
        patch("app.routes.market_routes.market_exists", AsyncMock(return_value=False)),
        patch(
            "app.routes.market_routes.create_market",
            AsyncMock(return_value={"id": 1, "marketName": "Test Market"}),
        ),
    ):
        result = await create_market_route(data, db, user)
    assert result["marketName"] == "Test Market"


@pytest.mark.asyncio
async def test_create_market_already_exists(db, user):
    data = MarketCreate(marketName="Test Market")
    with patch("app.routes.market_routes.market_exists", AsyncMock(return_value=True)):
        with pytest.raises(HTTPException) as exc:
            await create_market_route(data, db, user)
    assert exc.value.status_code == 400
    assert exc.value.detail == "Market already exists"


@pytest.mark.asyncio
async def test_my_market_found(db, user):
    mock_market = {"id": 1, "marketName": "Test"}
    with patch("app.routes.market_routes.get_my_market", AsyncMock(return_value=mock_market)):
        result = await my_market(db, user)
    assert result == mock_market


@pytest.mark.asyncio
async def test_my_market_not_found(db, user):
    with patch("app.routes.market_routes.get_my_market", AsyncMock(return_value=None)):
        result = await my_market(db, user)
    assert result == {"market": None}


@pytest.mark.asyncio
async def test_update_my_market_success(db, user):
    data = MarketUpdate(marketName="Updated")
    with patch(
        "app.routes.market_routes.update_market", AsyncMock(return_value=None)
    ) as mock_update:
        result = await update_my_market(data, db, user)
    mock_update.assert_awaited_once_with(db, user["userId"], data)
    assert result == {"success": True}
