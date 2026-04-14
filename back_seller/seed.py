import asyncio
import uuid
from decimal import Decimal

from jose import jwt
from sqlalchemy import delete

from app.database.base import Base
from app.database.session import AsyncSessionLocal, engine
from app.enums.product_category import ProductCategory
from app.models.market import Market
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.user import User
from app.security.jwt_dependency import ALGORITHM, SECRET_KEY


async def seed():

    print("Creating tables (if not exist)")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        print("Cleaning database...")

        await db.execute(delete(OrderItem))
        await db.execute(delete(Order))
        await db.execute(delete(Product))
        await db.execute(delete(Market))
        await db.execute(delete(User))
        await db.commit()

        print("Creating users")

        seller_id = uuid.uuid4()
        buyer_id = uuid.uuid4()

        seller = User(
            userId=seller_id,
            login="seller_test",
            passwordHash="hashed_password",
            firstName="Ivan",
            lastName="Petrov",
            city="Moscow",
            telegram="@seller",
            telegramChatId="123",
            isSeller=True,
        )

        buyer = User(
            userId=buyer_id,
            login="buyer_test",
            passwordHash="hashed_password",
            firstName="Anna",
            lastName="Ivanova",
            city="Berlin",
            telegram="@buyer",
            telegramChatId="456",
            isSeller=False,
        )

        db.add_all([seller, buyer])
        await db.commit()

        print("Users created")

        print("Creating seller market...")

        market = Market(
            userId=seller_id, marketName="Tech Store", description="Electronics and gadgets"
        )

        db.add(market)
        await db.commit()
        await db.refresh(market)

        print("Market created")

        print("Creating products")

        products = [
            Product(
                marketId=market.marketId,
                name="iPhone 15",
                description="Apple smartphone",
                category=ProductCategory.electronics,
                price=Decimal("999.99"),
                available=10,
                img="https://example.com/iphone.jpg",
            ),
            Product(
                marketId=market.marketId,
                name="MacBook Pro",
                description="Apple laptop",
                category=ProductCategory.electronics,
                price=Decimal("2499.99"),
                available=5,
                img="https://example.com/macbook.jpg",
            ),
            Product(
                marketId=market.marketId,
                name="Gaming Mouse",
                description="RGB gaming mouse",
                category=ProductCategory.electronics,
                price=Decimal("79.99"),
                available=25,
                img="https://example.com/mouse.jpg",
            ),
        ]

        db.add_all(products)
        await db.commit()

        print("Products created")

        print("Creating example orders")

        order1 = Order(
            marketId=market.marketId,
            userId=buyer_id,
            orderNumber="ORD-1001",
            deliveryAddress="Berlin, Main Street 10",
            totalAmount=Decimal("3199.98"),
            status=OrderStatus.processing,
        )

        db.add(order1)
        await db.commit()
        await db.refresh(order1)

        items = [
            OrderItem(
                orderId=order1.id, productId=products[0].id, quantity=1, price=products[0].price
            ),
            OrderItem(
                orderId=order1.id, productId=products[1].id, quantity=1, price=products[1].price
            ),
        ]

        db.add_all(items)
        await db.commit()

        print("Orders created")

        print("\nGenerating JWT token for seller")

        payload = {"sub": str(seller_id), "isSeller": True}
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        print(" SELLER JWT TOKEN:")
        print(" Bearer", token)
        print("Seller userId:", seller_id)


if __name__ == "__main__":
    asyncio.run(seed())
