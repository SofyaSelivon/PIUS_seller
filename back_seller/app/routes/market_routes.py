from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.market_controller import (
    create_market,
    get_my_market,
    market_exists,
    update_market,
)
from app.database.session import get_db
from app.schemas.market_schema import MarketCreate, MarketUpdate
from app.security.jwt_dependency import get_current_user

router = APIRouter(prefix="/api/markets", tags=["markets"])


@router.post("/create")
async def create_market_route(
    data: MarketCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)
):

    existing = await market_exists(db, user["userId"])
    if existing:
        raise HTTPException(status_code=400, detail="Market already exists")

    market = await create_market(db, user["userId"], data)
    return market


@router.get("/my")
async def my_market(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    market = await get_my_market(db, user["userId"])

    if not market:
        return {"market": None}

    return market


@router.patch("/my")
async def update_my_market(
    data: MarketUpdate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)
):
    await update_market(db, user["userId"], data)

    return {"success": True}
