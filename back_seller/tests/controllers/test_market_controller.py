import uuid

import pytest

from app.controllers.market_controller import get_my_market


@pytest.mark.asyncio
async def test_market_controller_empty(test_db):
    async with test_db() as db:
        result = await get_my_market(
            db,
            user_id=uuid.UUID("00000000-0000-0000-0000-000000000000")
        )
        assert result is None