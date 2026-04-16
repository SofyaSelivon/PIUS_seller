import uuid
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.user import User

router = APIRouter(prefix="/api/v1/internal/products", tags=["internal-products"])


class ProductsInfoRequest(BaseModel):
    productIds: list[UUID]


class ReserveItem(BaseModel):
    productId: UUID
    quantity: int


class ReserveRequest(BaseModel):
    items: list[ReserveItem]


@router.post("/info")
async def get_products_info(body: ProductsInfoRequest, db: AsyncSession = Depends(get_db)):
    ids = body.productIds

    result = await db.execute(select(Product).where(Product.id.in_(ids)))
    products = result.scalars().all()

    return [
        {
            "id": str(p.id),
            "name": p.name,
            "price": float(p.price),
            "available": p.available,
            "marketId": str(p.marketId),
        }
        for p in products
    ]


@router.post("/reserve")
async def reserve_products(body: ReserveRequest, db: AsyncSession = Depends(get_db)):
    product_ids = [item.productId for item in body.items]

    result = await db.execute(select(Product).where(Product.id.in_(product_ids)))
    products = result.scalars().all()
    products_map = {p.id: p for p in products}

    for item in body.items:
        product = products_map.get(item.productId)

        if product is None:
            raise HTTPException(status_code=400, detail=f"Товар {item.productId} не найден")

        if product.available < item.quantity:
            raise HTTPException(status_code=400, detail="Недостаточно товара на складе")

    for item in body.items:
        product = products_map[item.productId]
        new_amount = product.available - item.quantity

        await db.execute(
            Product.__table__.update()
            .where(Product.id == item.productId)
            .values(available=new_amount)
        )

    await db.commit()

    return {"success": True}


class CreateOrderInternal(BaseModel):
    marketId: UUID
    userId: UUID
    deliveryAddress: str
    totalAmount: float
    items: list[dict]


@router.post("/orders")
async def create_order_internal(data: CreateOrderInternal, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.userId == data.userId))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            userId=data.userId,
            login=f"user_{data.userId}",
            passwordHash="stub",
            firstName="stub",
            lastName="stub",
            isSeller=False,
        )
        db.add(user)
        await db.flush()

    order = Order(
        marketId=data.marketId,
        userId=data.userId,
        orderNumber=str(uuid.uuid4()),
        deliveryAddress=data.deliveryAddress,
        totalAmount=data.totalAmount,
        status=OrderStatus.pending,
    )

    db.add(order)
    await db.flush()

    for item in data.items:
        if "productId" not in item or "quantity" not in item or "price" not in item:
            raise HTTPException(
                status_code=400, detail="items must contain productId, quantity, price"
            )
        db.add(
            OrderItem(
                orderId=order.id,
                productId=UUID(item["productId"]),
                quantity=item["quantity"],
                price=item["price"],
            )
        )

    await db.commit()

    return {"success": True}
