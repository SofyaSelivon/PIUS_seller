from unittest.mock import AsyncMock, patch

import pytest

from app.database.session import get_db


@pytest.mark.asyncio
async def test_get_db_full_cycle():
    mock_session = AsyncMock()

    class MockSessionContext:
        async def __aenter__(self):
            return mock_session

        async def __aexit__(self, exc_type, exc, tb):
            pass

    with patch("app.database.session.AsyncSessionLocal", return_value=MockSessionContext()):
        gen = get_db()
        session = await gen.__anext__()
        assert session == mock_session
        with pytest.raises(StopAsyncIteration):
            await gen.__anext__()
