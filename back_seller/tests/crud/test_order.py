from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.crud.order import get_orders_with_stats, soft_delete_order, update_order_status
from app.models.order import OrderStatus


@pytest.fixture
def db():
    return AsyncMock()


@pytest.fixture
def market_id():
    return uuid4()


@pytest.mark.asyncio
async def test_get_orders_with_stats_success(db, market_id):
    order = MagicMock()
    order.id = uuid4()
    order.orderNumber = "ORD-1"
    order.deliveryAddress = "Address"
    order.totalAmount = 100.5
    order.status = OrderStatus.completed
    order.createdAt = datetime.now(UTC)

    row = (order, 3, "user1", "John", "Doe", None, "@john")

    total_orders_res = MagicMock()
    total_orders_res.scalar.return_value = 5

    revenue_res = MagicMock()
    revenue_res.scalar.return_value = 1000

    completed_res = MagicMock()
    completed_res.scalar.return_value = 2

    processing_res = MagicMock()
    processing_res.scalar.return_value = 1

    pending_res = MagicMock()
    pending_res.scalar.return_value = 2

    orders_res = MagicMock()
    orders_res.all.return_value = [row]

    db.execute.side_effect = [
        total_orders_res,
        revenue_res,
        completed_res,
        processing_res,
        pending_res,
        orders_res,
    ]
    result = await get_orders_with_stats(db, market_id)
    assert len(result["orders"]) == 1
    assert result["orders"][0]["itemsCount"] == 3
    assert result["orders"][0]["customer"]["fullName"] == "John Doe"
    assert result["statistics"]["totalOrders"] == 5
    assert result["statistics"]["totalRevenue"] == 1000.0


@pytest.mark.asyncio
async def test_get_orders_with_stats_empty(db, market_id):
    zero_res = MagicMock()
    zero_res.scalar.return_value = 0

    orders_res = MagicMock()
    orders_res.all.return_value = []

    db.execute.side_effect = [zero_res, zero_res, zero_res, zero_res, zero_res, orders_res]
    result = await get_orders_with_stats(db, market_id)
    assert result["orders"] == []
    assert result["statistics"]["totalOrders"] == 0
    assert result["pagination"]["total"] == 0


@pytest.mark.asyncio
async def test_get_orders_with_stats_full_name_building(db, market_id):
    order = MagicMock()
    order.id = uuid4()
    order.orderNumber = "ORD-2"
    order.deliveryAddress = "Addr"
    order.totalAmount = 50
    order.status = OrderStatus.pending
    order.createdAt = datetime.now(UTC)

    row = (order, 1, "user2", "Ivan", "Ivanov", "Ivanovich", None)

    stat_res = MagicMock()
    stat_res.scalar.return_value = 1

    orders_res = MagicMock()
    orders_res.all.return_value = [row]

    db.execute.side_effect = [stat_res, stat_res, stat_res, stat_res, stat_res, orders_res]
    result = await get_orders_with_stats(db, market_id)
    assert result["orders"][0]["customer"]["fullName"] == "Ivan Ivanov Ivanovich"


@pytest.mark.asyncio
async def test_get_orders_with_stats_pagination(db, market_id):
    stat_res = MagicMock()
    stat_res.scalar.return_value = 10

    orders_res = MagicMock()
    orders_res.all.return_value = []

    db.execute.side_effect = [stat_res, stat_res, stat_res, stat_res, stat_res, orders_res]
    result = await get_orders_with_stats(db, market_id, page=2, limit=5)
    assert result["pagination"]["total"] == 10


@pytest.mark.asyncio
async def test_update_order_status_success(db):
    order = MagicMock()
    order.status = OrderStatus.pending

    result = await update_order_status(db, order, OrderStatus.completed)
    assert order.status == OrderStatus.completed
    db.commit.assert_awaited_once()
    assert result is True


@pytest.mark.asyncio
async def test_update_order_status_overwrite(db):
    order = MagicMock()
    order.status = OrderStatus.processing
    await update_order_status(db, order, OrderStatus.cancelled)
    assert order.status == OrderStatus.cancelled


@pytest.mark.asyncio
async def test_update_order_status_commit_called(db):
    order = MagicMock()
    await update_order_status(db, order, OrderStatus.completed)
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_soft_delete_order_success(db):
    order = MagicMock()
    order.deletedAt = None
    result = await soft_delete_order(db, order)
    assert order.deletedAt is not None
    db.commit.assert_awaited_once()
    assert result is True


@pytest.mark.asyncio
async def test_soft_delete_order_sets_deletedAt(db):
    order = MagicMock()
    await soft_delete_order(db, order)
    assert order.deletedAt is not None


@pytest.mark.asyncio
async def test_soft_delete_order_commit_called(db):
    order = MagicMock()
    await soft_delete_order(db, order)
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_orders_with_stats_with_status_filter(db, market_id):
    stat_res = MagicMock()
    stat_res.scalar.return_value = 1

    orders_res = MagicMock()
    orders_res.all.return_value = []

    db.execute.side_effect = [stat_res, stat_res, stat_res, stat_res, stat_res, orders_res]
    result = await get_orders_with_stats(db, market_id, status=OrderStatus.completed)
    assert result["orders"] == []
