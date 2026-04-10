import pytest


@pytest.mark.asyncio
async def test_internal_products_info_empty(client):
    resp = await client.post(
        "/api/internal/products/info",
        json={"productIds": []}
    )
    assert resp.status_code == 200
    assert resp.json() == []