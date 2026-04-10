import pytest


@pytest.mark.asyncio
async def test_get_my_products_empty(client, seller_token):
    resp = await client.get(
        "/api/products/my",
        headers={"Authorization": f"Bearer {seller_token}"}
    )
    data = resp.json()
    assert data["items"] == []
    assert data["pagination"] == {}