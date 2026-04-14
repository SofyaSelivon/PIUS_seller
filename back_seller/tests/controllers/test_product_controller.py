from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.controllers.product_controller import (
    create_product,
    delete_product,
    get_my_products,
    get_product,
    update_product,
)
from app.models.market import Market
from app.models.product import Product


@pytest.fixture
def db():
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_db.execute.return_value = mock_result
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    return mock_db


@pytest.fixture
def user_id():
    return str(uuid4())


@pytest.fixture
def market_id():
    return uuid4()


@pytest.fixture
def product_id():
    return uuid4()


async def test_get_my_products_no_market(db, user_id):
    db.execute.return_value.scalars.return_value.first.return_value = None
    result = await get_my_products(
        db=db,
        user_id=user_id,
        page=1,
        limit=12,
        search=None,
        category=None,
        min_price=None,
        max_price=None,
        available=None,
    )
    assert result == {"items": [], "pagination": {"total": 0}}


async def test_get_my_products_with_filters(db, user_id, market_id):
    mock_market = MagicMock(spec=Market)
    mock_market.marketId = market_id

    mock_product = MagicMock(spec=Product)
    mock_product.id = uuid4()
    mock_product.name = "Test Product"
    mock_product.price = 999.99
    mock_product.description = "Desc"
    mock_product.category = "electronics"
    mock_product.available = 5
    mock_product.img = None
    market_res = MagicMock()
    market_res.scalars.return_value.first.return_value = mock_market

    count_res = MagicMock()
    count_res.scalar.return_value = 5

    products_res = MagicMock()
    products_res.scalars.return_value.all.return_value = [mock_product]

    db.execute.side_effect = [market_res, count_res, products_res]
    result = await get_my_products(
        db=db,
        user_id=user_id,
        page=1,
        limit=10,
        search="Test",
        category="electronics",
        min_price=500.0,
        max_price=1500.0,
        available=True,
    )
    assert len(result["items"]) == 1
    assert result["pagination"]["total"] == 5
    assert result["items"][0].name == "Test Product"


async def test_get_my_products_empty_result(db, user_id, market_id):
    mock_market = MagicMock(spec=Market)
    mock_market.marketId = market_id

    market_res = MagicMock()
    market_res.scalars.return_value.first.return_value = mock_market

    count_res = MagicMock()
    count_res.scalar.return_value = 0

    products_res = MagicMock()
    products_res.scalars.return_value.all.return_value = []

    db.execute.side_effect = [market_res, count_res, products_res]
    result = await get_my_products(
        db=db,
        user_id=user_id,
        page=1,
        limit=10,
        search=None,
        category=None,
        min_price=None,
        max_price=None,
        available=None,
    )
    assert result["items"] == []
    assert result["pagination"]["total"] == 0


async def test_create_product_success(db, user_id, market_id):
    mock_market = MagicMock(spec=Market)
    mock_market.marketId = market_id
    db.execute.return_value.scalars.return_value.first.return_value = mock_market

    class DummyData:
        name = "Новый товар"
        description = "Описание"
        category = "electronics"
        price = 2999.99
        available = 10
        img = "https://example.com/img.jpg"

    result = await create_product(db, user_id, DummyData())
    assert isinstance(result, Product)
    assert result.name == "Новый товар"
    assert float(result.price) == 2999.99
    assert result.available == 10
    db.add.assert_called_once()
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once()


async def test_create_product_no_market(db, user_id):
    db.execute.return_value.scalars.return_value.first.return_value = None

    class DummyData:
        pass

    with pytest.raises(HTTPException) as exc_info:
        await create_product(db, user_id, DummyData())
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Market not found"


async def test_create_product_minimal_data(db, user_id, market_id):
    mock_market = MagicMock(spec=Market)
    mock_market.marketId = market_id
    db.execute.return_value.scalars.return_value.first.return_value = mock_market

    class DummyData:
        name = "Минимальный товар"
        description = None
        category = "other"
        price = 100.0
        available = 1
        img = None

    result = await create_product(db, user_id, DummyData())
    assert isinstance(result, Product)
    assert result.name == "Минимальный товар"
    assert result.available == 1


async def test_get_product_success(db, user_id, market_id, product_id):
    mock_market = MagicMock(spec=Market)
    mock_market.marketId = market_id

    mock_product = MagicMock(spec=Product)
    mock_product.id = product_id

    market_res = MagicMock()
    market_res.scalars.return_value.first.return_value = mock_market

    product_res = MagicMock()
    product_res.scalars.return_value.first.return_value = mock_product

    db.execute.side_effect = [market_res, product_res]
    result = await get_product(db, product_id, user_id)
    assert result == mock_product


async def test_update_product_success(db, user_id, product_id):
    mock_product = MagicMock(spec=Product)
    mock_product.name = "Старое имя"
    mock_product.price = 1000

    async def mock_get_product(d, pid, uid):
        return mock_product

    db.commit = AsyncMock()
    db.refresh = AsyncMock(return_value=mock_product)

    class DummyData:
        name = "Новое имя"
        price = 1499.99
        available = None

    with patch("app.controllers.product_controller.get_product", mock_get_product):
        result = await update_product(db, product_id, user_id, DummyData())
    assert result == mock_product
    assert mock_product.name == "Новое имя"


async def test_delete_product_success(db, user_id, product_id):
    mock_product = MagicMock(spec=Product)

    async def mock_get_product(d, pid, uid):
        return mock_product

    db.delete = AsyncMock()
    db.commit = AsyncMock()

    with patch("app.controllers.product_controller.get_product", mock_get_product):
        await delete_product(db, product_id, user_id)
    db.delete.assert_awaited_once_with(mock_product)
    db.commit.assert_awaited_once()


async def test_update_product_available_only(db, user_id, product_id):
    mock_product = MagicMock(spec=Product)
    mock_product.name = "Old"

    async def mock_get_product(d, pid, uid):
        return mock_product

    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    class Dummy:
        name = None
        price = None
        available = 99

    with patch("app.controllers.product_controller.get_product", mock_get_product):
        result = await update_product(db, product_id, user_id, Dummy())

    assert mock_product.available == 99
    assert result == mock_product


async def test_update_product_price_only(db, user_id, product_id):
    mock_product = MagicMock(spec=Product)
    mock_product.price = 100

    async def mock_get_product(d, pid, uid):
        return mock_product

    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    class Dummy:
        name = None
        price = 555.55
        available = None

    with patch("app.controllers.product_controller.get_product", mock_get_product):
        result = await update_product(db, product_id, user_id, Dummy())

    assert float(mock_product.price) == 555.55
    assert result == mock_product


async def test_delete_product_not_found(db, user_id, product_id):
    async def mock_get_product(d, pid, uid):
        return None

    with patch("app.controllers.product_controller.get_product", mock_get_product):
        with pytest.raises(HTTPException) as exc:
            await delete_product(db, product_id, user_id)

    assert exc.value.status_code == 404


async def test_get_product_market_not_found(db, user_id, product_id):
    db.execute.side_effect = [
        MagicMock(scalars=lambda: MagicMock(first=lambda: None)),
    ]

    with pytest.raises(HTTPException) as exc:
        await get_product(db, product_id, user_id)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Market not found"


async def test_get_product_product_not_found(db, user_id, market_id, product_id):
    mock_market = MagicMock(spec=Market)
    mock_market.marketId = market_id

    market_res = MagicMock()
    market_res.scalars.return_value.first.return_value = mock_market

    product_res = MagicMock()
    product_res.scalars.return_value.first.return_value = None

    db.execute.side_effect = [market_res, product_res]

    with pytest.raises(HTTPException) as exc:
        await get_product(db, product_id, user_id)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Product not found"


async def test_get_my_products_available_false(db, user_id, market_id):
    mock_market = MagicMock(spec=Market)
    mock_market.marketId = market_id

    market_res = MagicMock()
    market_res.scalars.return_value.first.return_value = mock_market

    count_res = MagicMock()
    count_res.scalar.return_value = 1

    product = MagicMock(spec=Product)

    products_res = MagicMock()
    products_res.scalars.return_value.all.return_value = [product]

    db.execute.side_effect = [market_res, count_res, products_res]
    result = await get_my_products(
        db=db,
        user_id=user_id,
        page=1,
        limit=10,
        search=None,
        category=None,
        min_price=None,
        max_price=None,
        available=False,
    )
    assert len(result["items"]) == 1
