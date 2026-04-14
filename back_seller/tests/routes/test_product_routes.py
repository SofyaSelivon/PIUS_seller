from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.routes.product_routes import (
    create,
    delete_product_by_id,
    get_all_products,
    get_product_by_id,
    get_products_by_ids,
    my_products,
    update_product_by_id,
)
from app.schemas.product_schema import ProductCategory


@pytest.fixture
def db():
    return AsyncMock()


@pytest.fixture
def user():
    return {"userId": "test-user"}


@pytest.mark.asyncio
async def test_get_products_by_ids(db):
    product = MagicMock()
    product.id = uuid4()
    product.name = "Test"
    product.description = "Desc"
    product.category = "cat"
    product.price = 100
    product.img = None
    product.available = 5
    product.marketId = uuid4()

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [product]

    db.execute.return_value = mock_result
    result = await get_products_by_ids(data=MagicMock(productIds=[product.id]), db=db)
    assert len(result) == 1
    assert result[0]["name"] == "Test"


@pytest.mark.asyncio
async def test_my_products(db, user):
    with patch("app.routes.product_routes.get_my_products", new_callable=AsyncMock) as mock:
        mock.return_value = {"items": [], "pagination": {}}

        result = await my_products(
            page=1,
            limit=12,
            search=None,
            category=None,
            minPrice=None,
            maxPrice=None,
            available=None,
            db=db,
            user=user,
        )
    mock.assert_awaited_once()
    assert "items" in result


@pytest.mark.asyncio
async def test_get_all_products(db):
    from app.routes.product_routes import get_all_products

    product = MagicMock()
    product.id = uuid4()
    product.name = "Test"
    product.description = "Desc"
    product.category = "cat"
    product.price = 100
    product.img = None
    product.available = 5
    product.createdAt = "now"
    product.marketId = uuid4()

    count_result = MagicMock()
    count_result.scalar.return_value = 1

    products_result = MagicMock()
    products_result.scalars.return_value.all.return_value = [product]

    db.execute.side_effect = [count_result, products_result]
    result = await get_all_products(
        page=1,
        limit=12,
        search=None,
        category=None,
        minPrice=None,
        maxPrice=None,
        available=None,
        db=db,
    )
    assert result["pagination"]["totalItems"] == 1
    assert len(result["items"]) == 1
    assert result["items"][0]["name"] == "Test"


@pytest.mark.asyncio
async def test_create_product(db, user):
    product = MagicMock()
    product.id = uuid4()

    with patch("app.routes.product_routes.create_product", new_callable=AsyncMock) as mock:
        mock.return_value = product

        result = await create(data=MagicMock(), db=db, user=user)
    assert result["success"] is True
    assert "productId" in result


@pytest.mark.asyncio
async def test_get_product_by_id(db, user):
    product = {"id": "123"}

    with patch("app.routes.product_routes.get_product", new_callable=AsyncMock) as mock:
        mock.return_value = product
        result = await get_product_by_id(product_id=uuid4(), db=db, user=user)
    assert result == product


@pytest.mark.asyncio
async def test_update_product_by_id(db, user):
    with patch("app.routes.product_routes.update_product", new_callable=AsyncMock) as mock:
        mock.return_value = None

        result = await update_product_by_id(product_id=uuid4(), data=MagicMock(), db=db, user=user)
    mock.assert_awaited_once()
    assert result == {"success": True}


@pytest.mark.asyncio
async def test_delete_product_by_id(db, user):
    with patch("app.routes.product_routes.delete_product", new_callable=AsyncMock) as mock:
        mock.return_value = None
        result = await delete_product_by_id(product_id=uuid4(), db=db, user=user)
    mock.assert_awaited_once()
    assert result == {"success": True}


@pytest.mark.asyncio
async def test_get_all_products_empty(db):
    count_result = MagicMock()
    count_result.scalar.return_value = 0

    products_result = MagicMock()
    products_result.scalars.return_value.all.return_value = []

    db.execute.side_effect = [count_result, products_result]
    result = await get_all_products(
        page=1,
        limit=12,
        search=None,
        category=None,
        minPrice=None,
        maxPrice=None,
        available=None,
        db=db,
    )
    assert result["pagination"]["totalItems"] == 0
    assert result["items"] == []


@pytest.mark.asyncio
async def test_get_products_by_ids_empty(db):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    db.execute.return_value = mock_result
    result = await get_products_by_ids(data=MagicMock(productIds=[]), db=db)
    assert result == []


@pytest.mark.asyncio
async def test_get_product_by_id_not_found(db, user):
    with patch("app.routes.product_routes.get_product", new_callable=AsyncMock) as mock:
        mock.return_value = None
        result = await get_product_by_id(product_id=uuid4(), db=db, user=user)
    assert result is None or result == {"detail": "Product not found"}


@pytest.mark.asyncio
async def test_update_product_by_id_calls_update(db, user):
    with patch("app.routes.product_routes.update_product", new_callable=AsyncMock) as mock:
        mock.return_value = None
        data = MagicMock()
        pid = uuid4()
        await update_product_by_id(product_id=pid, data=data, db=db, user=user)
        mock.assert_awaited_once()
        args, kwargs = mock.call_args
        assert args[0] == db
        assert args[1] == pid
        assert args[2] == user["userId"]
        assert args[3] == data


@pytest.mark.asyncio
async def test_delete_product_by_id_calls(db, user):
    with patch("app.routes.product_routes.delete_product", new_callable=AsyncMock) as mock:
        mock.return_value = None
        pid = uuid4()
        await delete_product_by_id(product_id=pid, db=db, user=user)
        mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_all_products_with_search(db):
    count_result = MagicMock()
    count_result.scalar.return_value = 1

    products_result = MagicMock()
    products_result.scalars.return_value.all.return_value = []

    db.execute.side_effect = [count_result, products_result]
    await get_all_products(
        page=1,
        limit=10,
        search="test",
        category=None,
        minPrice=None,
        maxPrice=None,
        available=None,
        db=db,
    )
    assert db.execute.called


@pytest.mark.asyncio
async def test_get_all_products_with_category(db):
    count_result = MagicMock()
    count_result.scalar.return_value = 0

    products_result = MagicMock()
    products_result.scalars.return_value.all.return_value = []

    db.execute.side_effect = [count_result, products_result]
    await get_all_products(category=ProductCategory.food, db=db)


@pytest.mark.asyncio
async def test_get_all_products_with_price_filters(db):
    count_result = MagicMock()
    count_result.scalar.return_value = 0

    products_result = MagicMock()
    products_result.scalars.return_value.all.return_value = []

    db.execute.side_effect = [count_result, products_result]
    await get_all_products(minPrice=10, maxPrice=100, db=db)


@pytest.mark.asyncio
async def test_get_all_products_available_true(db):
    count_result = MagicMock()
    count_result.scalar.return_value = 0

    products_result = MagicMock()
    products_result.scalars.return_value.all.return_value = []

    db.execute.side_effect = [count_result, products_result]
    await get_all_products(available=True, db=db)


@pytest.mark.asyncio
async def test_get_all_products_available_false(db):
    count_result = MagicMock()
    count_result.scalar.return_value = 0

    products_result = MagicMock()
    products_result.scalars.return_value.all.return_value = []

    db.execute.side_effect = [count_result, products_result]
    await get_all_products(available=False, db=db)
