"""
Put here any Python code that must be runned before application startup.
It is included in `init.sh` script.

By default `main` create a admin if it does not exist.
"""

import asyncio
from typing import Optional

from fastapi_users.password import get_password_hash
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy import select

from app import schemas
from app.core import config
from app.models import UserTable
from app.session import async_session


async def main() -> None:
    print("Start initial data")
    async with async_session() as session:
        result = await session.execute(
            select(UserTable).where(
                UserTable.email == config.settings.FIRST_ADMIN_EMAIL
            )
        )
        user: Optional[UserTable] = result.scalars().first()

        if user is None:
            await SQLAlchemyUserDatabase(schemas.UserDB, session, UserTable).create(
                schemas.UserDB(
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
