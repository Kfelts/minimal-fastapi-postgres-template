"""
You can have several authentication methods, e.g. a cookie
authentication for browser-based queries and a JWT token authentication for pure API queries.

In this template, token will be sent through Bearer header
{"Authorization": "Bearer xyz"}
using JWT tokens.

There are more option to consider, refer to
https://fastapi-users.github.io/fastapi-users/configuration/authentication/

UserManager class is core fastapi users class with customizable attrs and methods
https://fastapi-users.github.io/fastapi-users/configuration/user-manager/
"""
import uuid
from typing import Optional

from fastapi import Request, Depends
from fastapi_users.fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    CookieTransport,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.manager import BaseUserManager, UUIDIDMixin
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from passlib.context import CryptContext

from app.models import User, OAuthAccount
from app.core import config
from app.api.deps import get_user_db

SECRET = config.settings.SECRET_KEY
pwd_context = CryptContext(schemes=["sha256_crypt", "md5_crypt"])

cookie_transport = CookieTransport(cookie_samesite="none")
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=SECRET,
        lifetime_seconds=config.settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

jwt_backend = AuthenticationBackend(
    name="bearer-jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

cookie_backend = AuthenticationBackend(
    name="cookie-jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

async def get_enabled_backends(request: Request):
    if request.url.path == ["/auth/jwt", "/auth/facebook", "/auth/github", "/auth/google"]:
        return [jwt_backend]
    else:
        return [cookie_backend, jwt_backend]

class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(self, user: User, token: str, request: Optional[Request] = None):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(self, user: User, token: str, request: Optional[Request] = None):
        print(f"Verification requested for user {user.id}. Verification token: {token}")

async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)

fastapi_users = FastAPIUsers[User, OAuthAccount, uuid.UUID](
    get_user_manager,  # type: ignore
    get_enabled_backends
)

current_user = fastapi_users.current_user()
current_active_user = fastapi_users.current_user(active=True, get_enabled_backends=get_enabled_backends)
current_admin = fastapi_users.current_user(active=True, admin=True)
