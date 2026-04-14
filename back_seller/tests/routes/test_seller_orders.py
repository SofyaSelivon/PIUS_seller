from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.models.order import OrderStatus
from app.routes.seller_orders import (
    delete_order,
    get_completed_orders,
    get_order_by_id,
    get_revenue,
    get_total_revenue,
    list_orders,
    update_status,
)
from app.schemas.order import OrderStatusUpdate


def make_scalar(value):
    m = MagicMock()
    m.scalar.return_value = value
    return m


@pytest.fixture
def db():
    return AsyncMock()


@pytest.fixture
def user():
    return {"userId": "test-user"}


@pytest.mark.asyncio
async def test_list_orders_no_market(db, user):
    db.execute.return_value = make_scalar(None)
    result = await list_orders(db=db, current_user=user)
    assert result["orders"] == []
    assert result["pagination"]["totalItems"] == 0


@pytest.mark.asyncio
async def test_list_orders_success(db, user, monkeypatch):
    db.execute.return_value = make_scalar(uuid4())
    monkeypatch.setattr(
        "app.routes.seller_orders.crud_order.get_orders_with_stats",
        AsyncMock(return_value={"orders": [1], "pagination": {"totalItems": 1}}),
    )
    result = await list_orders(db=db, current_user=user)
    assert result["orders"] == [1]


@pytest.mark.asyncio
async def test_get_revenue_empty(db, user):
    db.execute.return_value = make_scalar(None)
    result = await get_revenue(db=db, current_user=user)
    assert result == []


@pytest.mark.asyncio
async def test_get_revenue_success(db, user):
    db.execute.side_effect = [
        make_scalar(uuid4()),
        MagicMock(
            all=lambda: [
                MagicMock(date="2026-01-01", revenue=100),
                MagicMock(date="2026-01-02", revenue=None),
            ]
        ),
    ]

    result = await get_revenue(db=db, current_user=user)
    assert result[0]["revenue"] == 100.0
    assert result[1]["revenue"] == 0.0


@pytest.mark.asyncio
async def test_get_total_revenue(db, user):
    db.execute.side_effect = [
        make_scalar(uuid4()),
        make_scalar(500),
    ]
    result = await get_total_revenue(db=db, current_user=user)
    assert result["totalRevenue"] == 500.0


@pytest.mark.asyncio
async def test_get_total_revenue_empty(db, user):
    db.execute.return_value = make_scalar(None)
    result = await get_total_revenue(db=db, current_user=user)
    assert result["totalRevenue"] == 0


@pytest.mark.asyncio
async def test_get_completed_orders(db, user):
    db.execute.side_effect = [
        make_scalar(uuid4()),
        make_scalar(7),
    ]
    result = await get_completed_orders(db=db, current_user=user)
    assert result["completedOrders"] == 7


@pytest.mark.asyncio
async def test_update_status_success(db, user, monkeypatch):
    order = MagicMock()
    order.status = OrderStatus.pending
    db.execute.side_effect = [
        make_scalar(uuid4()),
        make_scalar(order),
    ]
    monkeypatch.setattr("app.routes.seller_orders.crud_order.update_order_status", AsyncMock())
    update = OrderStatusUpdate(status=OrderStatus.processing)
    result = await update_status(order_id=uuid4(), status_update=update, db=db, current_user=user)
    assert result["success"] is True


@pytest.mark.asyncio
async def test_delete_order_success(db, user, monkeypatch):
    order = MagicMock()
    db.execute.side_effect = [
        make_scalar(uuid4()),
        make_scalar(order),
    ]
    monkeypatch.setattr("app.routes.seller_orders.crud_order.soft_delete_order", AsyncMock())
    result = await delete_order(order_id=uuid4(), db=db, current_user=user)
    assert result["success"] is True


@pytest.mark.asyncio
async def test_get_order_by_id_success(db, user):
    order = MagicMock()
    order.id = uuid4()
    order.orderNumber = "123"
    order.deliveryAddress = "addr"
    order.totalAmount = 100
    order.status = OrderStatus.pending
    order.createdAt = "now"

    item = MagicMock()
    item.productId = uuid4()
    item.quantity = 2
    item.price = 50

    db.execute.side_effect = [
        make_scalar(uuid4()),
        make_scalar(order),
        MagicMock(scalars=lambda: MagicMock(all=lambda: [item])),
    ]
    result = await get_order_by_id(order_id=uuid4(), db=db, current_user=user)
    assert result["orderNumber"] == "123"
    assert len(result["items"]) == 1


@pytest.mark.asyncio
async def test_list_orders_no_market_returns_empty(db, user):
    db.execute.return_value = make_scalar(None)
    result = await list_orders(db=db, current_user=user)
    assert result["orders"] == []
    assert result["pagination"]["totalItems"] == 0
    assert "limit" in result["pagination"]


@pytest.mark.asyncio
async def test_get_revenue_empty_rows(db, user):
    db.execute.side_effect = [make_scalar(uuid4()), MagicMock(all=lambda: [])]
    result = await get_revenue(db=db, current_user=user)
    assert result == []


@pytest.mark.asyncio
async def test_get_total_revenue_none(db, user):
    db.execute.side_effect = [
        make_scalar(uuid4()),
        make_scalar(None),
    ]
    result = await get_total_revenue(db=db, current_user=user)
    assert result["totalRevenue"] == 0.0


@pytest.mark.asyncio
async def test_get_completed_orders_none(db, user):
    db.execute.side_effect = [
        make_scalar(uuid4()),
        make_scalar(None),
    ]
    result = await get_completed_orders(db=db, current_user=user)
    assert result["completedOrders"] == 0


@pytest.mark.asyncio
async def test_update_status_order_not_found(db, user):
    db.execute.side_effect = [
        make_scalar(uuid4()),
        make_scalar(None),
    ]
    with pytest.raises(HTTPException) as exc:
        await update_status(
            order_id=uuid4(),
            status_update=OrderStatusUpdate(status=OrderStatus.processing),
            db=db,
            current_user=user,
        )
    assert exc.value.status_code == 404
    assert str(exc.value.detail) == "Order not found"


@pytest.mark.asyncio
async def test_get_order_by_id_not_found(db, user):
    db.execute.side_effect = [
        make_scalar(uuid4()),
        make_scalar(None),
    ]
    with pytest.raises(HTTPException) as exc:
        await get_order_by_id(order_id=uuid4(), db=db, current_user=user)
    assert exc.value.status_code == 404
    assert exc.value.detail == "Order not found"


@pytest.mark.asyncio
async def test_update_status_no_body(db, user):
    db.execute.side_effect = [
        make_scalar(uuid4()),
    ]
    with pytest.raises(HTTPException) as exc:
        await update_status(order_id=uuid4(), status_update=None, db=db, current_user=user)
    assert exc.value.status_code == 400
    assert exc.value.detail == "Status body is required"


@pytest.mark.asyncio
async def test_update_status_invalid_transition(db, user):
    order = MagicMock()
    order.status = OrderStatus.pending

    db.execute.side_effect = [
        make_scalar(uuid4()),
        make_scalar(order),
    ]
    update = OrderStatusUpdate(status=OrderStatus.completed)
    with pytest.raises(HTTPException) as exc:
        await update_status(order_id=uuid4(), status_update=update, db=db, current_user=user)
    assert exc.value.status_code == 400
    assert exc.value.detail == "Invalid status transition"


@pytest.mark.asyncio
async def test_update_status_no_market(db, user):
    db.execute.return_value = make_scalar(None)

    with pytest.raises(HTTPException) as exc:
        await update_status(
            order_id=uuid4(),
            status_update=OrderStatusUpdate(status=OrderStatus.processing),
            db=db,
            current_user=user,
        )
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_order_not_found(db, user):
    db.execute.side_effect = [
        make_scalar(uuid4()),
        make_scalar(None),
    ]
    with pytest.raises(HTTPException) as exc:
        await delete_order(order_id=uuid4(), db=db, current_user=user)
    assert exc.value.status_code == 404
    assert exc.value.detail == "Order not found"


@pytest.mark.asyncio
async def test_update_status_no_market_and_no_order(db, user):
    db.execute.side_effect = [
        make_scalar(None),
        make_scalar(None),
    ]
    with pytest.raises(HTTPException) as exc:
        await update_status(
            order_id=uuid4(),
            status_update=OrderStatusUpdate(status=OrderStatus.processing),
            db=db,
            current_user=user,
        )
    assert exc.value.status_code == 404
    assert exc.value.detail == "Order not found"


@pytest.mark.asyncio
async def test_update_status_no_body_clean(db, user):
    with pytest.raises(HTTPException) as exc:
        await update_status(order_id=uuid4(), status_update=None, db=db, current_user=user)
    assert exc.value.status_code == 400
    assert exc.value.detail == "Status body is required"


@pytest.mark.asyncio
async def test_update_status_no_body_direct():
    from app.routes import seller_orders

    with pytest.raises(HTTPException):
        await seller_orders.update_status(
            order_id=uuid4(), status_update=None, db=AsyncMock(), current_user={"userId": "x"}
        )
