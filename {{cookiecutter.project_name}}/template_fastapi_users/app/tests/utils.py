import random
import string

from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from pydantic.networks import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.models import User


def random_lower_string(length: int = 32) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=length))


def random_email(length: int = 10) -> str:
    return f"{random_lower_string(length)}@{random_lower_string(length)}.com"


async def create_db_user(
    email: str,
    hashed_password: str,
    session: AsyncSession,
    is_admin: bool = False,
    is_verified: bool = True,
) -> schemas.UserCreate:

    new_user = await SQLAlchemyUserDatabase(schemas.UserDB, session, User).create(
        schemas.UserCreate(
            email=EmailStr(email),
            is_admin=is_admin,
            is_verified=is_verified,
            hashed_password=hashed_password,
        )
    )
    return new_user
