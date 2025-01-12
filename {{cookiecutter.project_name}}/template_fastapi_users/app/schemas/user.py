"""
All fields in schemas are defaults from FastAPI Users, repeated below for easier view
"""

import uuid
from typing import Optional

from fastapi_users import schemas 
from pydantic import UUID4, EmailStr, Field

class UserRead(schemas.BaseUser[uuid.UUID]):
    id: UUID4 = Field(default_factory=uuid.uuid4)
    email: EmailStr
    is_active: bool = True
    is_admin: bool = False
    is_verified: bool = False


class UserCreate(schemas.BaseUserCreate):
    email: EmailStr
    password: str
    is_active: Optional[bool] = True
    is_admin: Optional[bool] = False
    is_verified: Optional[bool] = False


class UserUpdate(schemas.BaseUserUpdate):
    password: Optional[str]
    email: Optional[EmailStr]
    is_active: Optional[bool]
    is_admin: Optional[bool]
    is_verified: Optional[bool]

