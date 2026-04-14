import logging
import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.controllers import market_controller as mc

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


def mock_scalar_first(value):
    result = MagicMock()
    result.scalars.return_value.first.return_value = value
    return result


def mock_scalar_one_or_none(value):
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    return result


def make_market():
    m = MagicMock()
    m.marketId = uuid.uuid4()
    m.marketName = "Old"
    m.description = "OldDesc"
    return m


def make_db():
    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.execute = AsyncMock()
    return db


@pytest.mark.asyncio
async def test_create_market_success():
    log.info("\nTEST: create_market_success")

    db = make_db()
    user_id = str(uuid.uuid4())

    data = MagicMock()
    data.marketName = "Test Market"
    data.description = "Desc"

    result = await mc.create_market(db, user_id, data)

    assert result.marketName == "Test Market"
    assert result.userId == user_id

    db.add.assert_called_once()
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once()

    added_obj = db.add.call_args[0][0]
    assert added_obj.marketName == "Test Market"
    assert added_obj.userId == user_id

    log.info("create_market OK")


@pytest.mark.asyncio
async def test_create_market_db_error():
    log.info("\nTEST: create_market_db_error")

    db = make_db()
    db.commit.side_effect = Exception("DB error")

    user_id = str(uuid.uuid4())

    data = MagicMock()
    data.marketName = "Test"
    data.description = "Desc"

    with pytest.raises(Exception):
        await mc.create_market(db, user_id, data)

    log.info("exception handled")


@pytest.mark.asyncio
async def test_create_market_generates_uuid():
    log.info("\nTEST: create_market_generates_uuid")

    db = make_db()
    user_id = str(uuid.uuid4())

    data = MagicMock()
    data.marketName = "Test"
    data.description = "Desc"

    result = await mc.create_market(db, user_id, data)
    assert result.marketId is not None
    assert len(str(result.marketId)) > 0

    log.info("uuid exists")


@pytest.mark.asyncio
async def test_get_my_market_success():
    log.info("\nTEST: get_my_market_success")

    db = make_db()
    user_id = str(uuid.uuid4())

    market = make_market()
    db.execute.return_value = mock_scalar_first(market)

    res = await mc.get_my_market(db, user_id)

    assert res == market
    db.execute.assert_awaited_once()

    log.info("✔ market fetched")


@pytest.mark.asyncio
async def test_get_my_market_not_found():
    log.info("\nTEST: get_my_market_not_found")

    db = make_db()
    user_id = str(uuid.uuid4())

    db.execute.return_value = mock_scalar_first(None)

    with pytest.raises(HTTPException) as exc:
        await mc.get_my_market(db, user_id)

    assert exc.value.status_code == 404

    log.info("404 raised")


@pytest.mark.asyncio
async def test_get_my_market_calls_db_once():
    log.info("\nTEST: get_my_market_calls_db_once")

    db = make_db()
    user_id = str(uuid.uuid4())

    db.execute.return_value = mock_scalar_first(make_market())

    await mc.get_my_market(db, user_id)

    assert db.execute.await_count == 1

    log.info("db executed once")


@pytest.mark.asyncio
async def test_update_market_success():
    log.info("\nTEST: update_market_success")

    db = make_db()
    user_id = str(uuid.uuid4())

    market = make_market()
    db.execute.return_value = mock_scalar_first(market)

    data = MagicMock()
    data.market_name = "New Name"
    data.description = "New Desc"

    await mc.update_market(db, user_id, data)

    assert market.marketName == "New Name"
    assert market.description == "New Desc"

    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once()

    log.info("update success")


@pytest.mark.asyncio
async def test_update_market_partial():
    log.info("\nTEST: update_market_partial")

    db = make_db()
    user_id = str(uuid.uuid4())

    market = make_market()
    db.execute.return_value = mock_scalar_first(market)

    data = MagicMock()
    data.market_name = None
    data.description = "Only Desc"

    await mc.update_market(db, user_id, data)

    assert market.marketName == "Old"
    assert market.description == "Only Desc"

    log.info("partial update")


@pytest.mark.asyncio
async def test_update_market_no_changes():
    log.info("\nTEST: update_market_no_changes")

    db = make_db()
    user_id = str(uuid.uuid4())

    market = make_market()
    db.execute.return_value = mock_scalar_first(market)

    data = MagicMock()
    data.market_name = None
    data.description = None

    await mc.update_market(db, user_id, data)

    assert market.marketName == "Old"
    assert market.description == "OldDesc"

    db.commit.assert_awaited_once()

    log.info("no changes case")


@pytest.mark.asyncio
async def test_update_market_not_found():
    log.info("\nTEST: update_market_not_found")

    db = make_db()
    user_id = str(uuid.uuid4())

    db.execute.return_value = mock_scalar_first(None)

    data = MagicMock()
    data.market_name = "kjsnkd"
    data.description = "s;dkvnd"

    with pytest.raises(HTTPException) as exc:
        await mc.update_market(db, user_id, data)

    assert exc.value.status_code == 404

    log.info("404 update")


@pytest.mark.asyncio
async def test_market_exists_true():
    log.info("\nTEST: market_exists_true")

    db = make_db()
    user_id = str(uuid.uuid4())

    market = make_market()
    db.execute.return_value = mock_scalar_one_or_none(market)

    res = await mc.market_exists(db, user_id)

    assert res == market

    log.info("exists true")


@pytest.mark.asyncio
async def test_market_exists_false():
    log.info("\nTEST: market_exists_false")

    db = make_db()
    user_id = str(uuid.uuid4())

    db.execute.return_value = mock_scalar_one_or_none(None)

    res = await mc.market_exists(db, user_id)

    assert res is None

    log.info("exists false")


@pytest.mark.asyncio
async def test_market_exists_db_error():
    log.info("\nTEST: market_exists_db_error")

    db = make_db()
    db.execute.side_effect = Exception("fail")

    with pytest.raises(Exception):
        await mc.market_exists(db, str(uuid.uuid4()))

    log.info("db error")
