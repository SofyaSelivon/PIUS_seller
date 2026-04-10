from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import jwt, JWTError

from app.config import SECRET_KEY, ALGORITHM

security = HTTPBearer()


async def get_current_user(credentials=Depends(security)):
    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id_str = payload.get("sub")

        if user_id_str is None:
            raise credentials_exception

        try:
            user_id = UUID(user_id_str)
        except ValueError:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    return {
        "userId": user_id,
    }