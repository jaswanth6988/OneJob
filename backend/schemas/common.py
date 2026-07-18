from typing import List, Generic, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    pages: int

class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Success"
    data: Optional[T] = None

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[Any] = None
