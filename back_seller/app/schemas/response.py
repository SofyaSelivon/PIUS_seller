from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiError(BaseModel):
    code: str
    message: str
    meta: Dict[str, Any] = {}


class ApiResponse(BaseModel, Generic[T]):
    data: Optional[T] = None
    errors: List[ApiError] = []
    meta: Dict[str, Any] = {}

    class Config:
        from_attributes = True
