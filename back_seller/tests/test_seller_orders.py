import pytest


@pytest.mark.asyncio
async def test_seller_orders_empty(client, seller_token):
    resp = await client.get(
        "/api/seller/orders",
        headers={"Authorization": f"Bearer {seller_token}"}
    )
    assert resp.status_code == 200

    data = resp.json()
    assert data["statistics"]["totalOrders"] == 0
    assert data["orders"] == []