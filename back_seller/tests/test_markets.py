import pytest


@pytest.mark.asyncio
async def test_get_my_market_empty(client, seller_token):
    resp = await client.get(
        "/api/markets/my",
        headers={"Authorization": f"Bearer {seller_token}"}
    )
    assert resp.status_code == 200
    assert resp.json() == {"market": None}