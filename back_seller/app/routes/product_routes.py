from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.product_controller import (
    create_product,
    delete_product,
    get_my_products,
    get_product,
    update_product,
)
from app.database.session import get_db
from app.models.product import Product
from app.schemas.product_schema import ProductCategory, ProductCreate, ProductUpdate
from app.security.jwt_dependency import get_current_user

router = APIRouter(prefix="/api/v1/products", tags=["products"])


class ProductsByIdsRequest(BaseModel):
    productIds: List[UUID]


@router.post("/by-ids")
async def get_products_by_ids(
    data: ProductsByIdsRequest,
    db: AsyncSession = Depends(get_db),
):
    query = select(Product).where(Product.id.in_(data.productIds))
    result = await db.execute(query)
    products = result.scalars().all()

    return [
        {
            "id": str(p.id),
            "name": p.name,
            "description": p.description,
            "category": p.category,
            "price": float(p.price),
            "img": p.img,
            "available": p.available,
            "marketId": str(p.marketId),
        }
        for p in products
    ]


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
    user=Depends(get_current_user),
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
        available=available,
    )


@router.get("/")
async def get_all_products(
    page: int = 1,
    limit: int = 12,
    search: str | None = None,
    category: ProductCategory | None = None,
    minPrice: float | None = None,
    maxPrice: float | None = None,
    available: bool | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Product)

    if search:
        query = query.where(Product.name.ilike(f"%{search}%"))

    if category:
        query = query.where(Product.category == category)

    if minPrice is not None:
        query = query.where(Product.price >= minPrice)

    if maxPrice is not None:
        query = query.where(Product.price <= maxPrice)

    if available is True:
        query = query.where(Product.available > 0)

    if available is False:
        query = query.where(Product.available == 0)

    count_query = select(func.count()).select_from(query.subquery())
    total_items = (await db.execute(count_query)).scalar()

    offset = (page - 1) * limit
    result = await db.execute(query.offset(offset).limit(limit))
    products = result.scalars().all()

    total_pages = (total_items + limit - 1) // limit if total_items else 1

    return {
        "items": [
            {
                "id": str(p.id),
                "name": p.name,
                "description": p.description,
                "category": p.category,
                "price": float(p.price),
                "img": p.img,
                "available": p.available,
                "createdAt": p.createdAt,
                "marketId": str(p.marketId),
            }
            for p in products
        ],
        "pagination": {
            "page": page,
            "limit": limit,
            "totalItems": total_items,
            "totalPages": total_pages,
        },
    }


@router.post("/")
async def create(
    data: ProductCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)
):
    product = await create_product(db, user["userId"], data)

    return {"success": True, "productId": product.id}


@router.get("/{product_id}")
async def get_product_by_id(
    product_id: UUID, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)
):
    product = await get_product(db, product_id, user["userId"])

    return product


@router.patch("/{product_id}")
async def update_product_by_id(
    product_id: UUID,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    await update_product(db, product_id, user["userId"], data)

    return {"success": True}


@router.delete("/{product_id}")
async def delete_product_by_id(
    product_id: UUID, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)
):
    await delete_product(db, product_id, user["userId"])

    return {"success": True}
