from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from jose import jwt

security = HTTPBearer()

SECRET_KEY = "super-secret-key-for-local-dev"
ALGORITHM = "HS256"


def get_current_user(credentials=Depends(security)):

    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        raise HTTPException(401, "Invalid token")

    if not payload.get("isSeller"):
        raise HTTPException(403, "User is not seller")

    try:
        user_id = UUID(payload["userId"])
    except Exception:
        raise HTTPException(401, "Invalid userId")

    return {
        "userId": user_id,
        "isSeller": payload["isSeller"]
    }