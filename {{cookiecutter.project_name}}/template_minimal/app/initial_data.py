"""
Put here any Python code that must be runned before application startup.
It is included in `init.sh` script.

By default `main` create a admin if not exists
"""

import asyncio

from sqlalchemy import select

from app.core import config, security
from app.core.session import async_session
from app.models import User


async def main() -> None:
    print("Start initial data")
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.email == config.settings.FIRST_ADMIN_EMAIL)
        )
        user: User | None = result.scalars().first()

        if user is None:
            new_admin = User(
                email=config.settings.FIRST_ADMIN_EMAIL,
                hashed_password=security.get_password_hash(
                    config.settings.FIRST_ADMIN_PASSWORD
                ),
            )
            session.add(new_admin)
            await session.commit()
            print("Admin was created")
        else:
            print("Admin already exists in database")

        print("Initial data created")


if __name__ == "__main__":
    asyncio.run(main())
