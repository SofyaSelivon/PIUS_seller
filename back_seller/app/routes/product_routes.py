from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.product_controller import (
    get_my_products,
    create_product,
    get_product,
    update_product,
    delete_product,
)
from app.database.session import get_db
from app.schemas.product_schema import ( 
    ProductUpdate, 
    ProductCategory, 
    ProductCreate
)
from app.security.jwt_dependency import get_current_user

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("/my")
async def my_products(
    page: int = 1,
    limit: int = 12,
    search: str | None = None,
    category: ProductCategory | None = None,
    minPrice: float | None = None,
    maxPrice: float | None = None,
    available: bool | None = None,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):

    return await get_my_products(
        db=db,
        user_id=user["userId"],
        page=page,
        limit=limit,
        search=search,
        category=category,
        min_price=minPrice,
        max_price=maxPrice,
        available=available
    )


@router.post("/")
async def create(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):

    product = await create_product(db, user["userId"], data)

    return {
        "success": True,
        "productId": product.id
    }


@router.get("/{product_id}")
async def get_product_by_id(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):

    product = await get_product(db, product_id, user["userId"])

    return product


@router.patch("/{product_id}")
async def update_product_by_id(
    product_id: UUID,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):

    await update_product(db, product_id, user["userId"], data)

    return {"success": True}


@router.delete("/{product_id}")
async def delete_product_by_id(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):

    await delete_product(db, product_id, user["userId"])

    return {"success": True}