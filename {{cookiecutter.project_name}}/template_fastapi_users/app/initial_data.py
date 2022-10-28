"""
Put here any Python code that must be run before application startup.
It is included in `init.sh` script.

By default `main` create an admin if it does not exist.
"""

import asyncio
from typing import Optional

from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy import select

from app import schemas
from app.core import config
from app.models import User
from app.session import async_session
from app.core.security import get_password_hash


async def main() -> None:
    print("Start initial data")
    async with async_session() as session:
        result = await session.execute(
            select(User).where(
                User.email == config.settings.FIRST_ADMIN_EMAIL
            )
        )
        user: Optional[User] = result.scalars().first()

        if user is None:
            await SQLAlchemyUserDatabase(session, User).create(
                schemas.UserCreate(
                    email=config.settings.FIRST_ADMIN_EMAIL,
                    is_admin=True,
                    is_verified=True,
                    hashed_password=get_password_hash(
                        config.settings.FIRST_ADMIN_PASSWORD
                    ),
                )
            )
            print("Admin was created")
        else:
            print("Admin already exists in database")

        print("Initial data created")


if __name__ == "__main__":
    asyncio.run(main())
