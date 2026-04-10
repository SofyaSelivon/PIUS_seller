import uuid

import pytest

from app.crud.order import get_orders_with_stats


@pytest.mark.asyncio
async def test_order_crud_empty(test_db):
    async with test_db() as db:
        result = await get_orders_with_stats(
            db,
            market_id=uuid.UUID("00000000-0000-0000-0000-000000000000")
        )
        assert result["statistics"]["totalOrders"] == 0