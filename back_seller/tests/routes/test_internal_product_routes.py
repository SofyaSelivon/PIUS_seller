from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.models.product import Product
from app.models.user import User
from app.routes.internal_product_routes import (
    CreateOrderInternal,
    ProductsInfoRequest,
    ReserveItem,
    ReserveRequest,
    create_order_internal,
    get_products_info,
    reserve_products,
)


@pytest.fixture
def db():
    mock = AsyncMock()
    mock.add = MagicMock()
    mock.commit = AsyncMock()
    mock.flush = AsyncMock()
    return mock


@pytest.mark.asyncio
async def test_get_products_info_success(db):
    product = MagicMock(spec=Product)
    product.id = uuid4()
    product.name = "Test"
    product.price = 100.0
    product.available = 5
    product.marketId = uuid4()

    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = [product]

    db.execute.return_value = result_mock
    body = ProductsInfoRequest(productIds=[product.id])
    res = await get_products_info(body, db)
    assert len(res) == 1
    assert res[0]["name"] == "Test"
    assert res[0]["available"] == 5


@pytest.mark.asyncio
async def test_get_products_info_empty(db):
    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = []
    db.execute.return_value = result_mock
    body = ProductsInfoRequest(productIds=[uuid4()])
    res = await get_products_info(body, db)
    assert res == []


@pytest.mark.asyncio
async def test_reserve_products_success(db):
    pid = uuid4()

    product = MagicMock(spec=Product)
    product.id = pid
    product.available = 10

    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = [product]
    db.execute.side_effect = [
        result_mock,
        MagicMock(),
    ]
    body = ReserveRequest(items=[ReserveItem(productId=pid, quantity=3)])
    res = await reserve_products(body, db)
    assert res["success"] is True
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_reserve_products_not_found(db):
    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = []

    db.execute.return_value = result_mock
    body = ReserveRequest(items=[ReserveItem(productId=uuid4(), quantity=1)])
    with pytest.raises(HTTPException) as exc:
        await reserve_products(body, db)
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_reserve_products_not_enough(db):
    pid = uuid4()

    product = MagicMock(spec=Product)
    product.id = pid
    product.available = 1

    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = [product]

    db.execute.return_value = result_mock
    body = ReserveRequest(items=[ReserveItem(productId=pid, quantity=5)])
    with pytest.raises(HTTPException) as exc:
        await reserve_products(body, db)
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_create_order_internal_existing_user(db):
    user = MagicMock(spec=User)

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = user

    db.execute.return_value = result_mock
    data = CreateOrderInternal(
        marketId=uuid4(),
        userId=uuid4(),
        deliveryAddress="Address",
        totalAmount=100.0,
        items=[{"productId": str(uuid4()), "quantity": 2, "price": 50.0}],
    )
    res = await create_order_internal(data, db)
    assert res["success"] is True
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_order_internal_create_user(db):
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None

    db.execute.return_value = result_mock
    data = CreateOrderInternal(
        marketId=uuid4(),
        userId=uuid4(),
        deliveryAddress="Address",
        totalAmount=200.0,
        items=[{"productId": str(uuid4()), "quantity": 1, "price": 200.0}],
    )
    res = await create_order_internal(data, db)
    assert db.add.called
    db.commit.assert_awaited_once()
    assert res["success"] is True
