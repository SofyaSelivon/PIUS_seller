
async def test_jwt_ok(client, seller_token):
    response = await client.get(
        "/api/products/my",
        headers={"Authorization": f"Bearer {seller_token}"}
    )
    assert response.status_code == 200


async def test_jwt_invalid_token(client, bad_token):
    response = await client.get(
        "/api/products/my",
        headers={"Authorization": f"Bearer {bad_token}"}
    )
    assert response.status_code == 401


async def test_jwt_not_seller(client, non_seller_token):
    response = await client.get(
        "/api/products/my",
        headers={"Authorization": f"Bearer {non_seller_token}"}
    )
    assert response.status_code == 403