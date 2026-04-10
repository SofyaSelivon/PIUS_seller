import uuid

import pytest

from app.controllers.product_controller import get_my_products


@pytest.mark.asyncio
async def test_product_controller_empty(test_db):
    async with test_db() as db:
        result = await get_my_products(
            db=db,
            user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
            page=1,
            limit=10,
            search=None,
            category=None,
            min_price=None,
            max_price=None,
            available=None
        )
        assert result["items"] == []