"""
Users and auth routers & oauth login endpoints

fastapi_users in defined in deps, because it also
includes useful dependencies.
"""

from fastapi import APIRouter, Depends
from app.core.security import fastapi_users, jwt_backend, cookie_backend, current_active_user
from app.core.config import settings
from app.models import User
from app.schemas.user import UserRead, UserCreate, UserUpdate
from httpx_oauth.oauth2 import OAuth2
from httpx_oauth.integrations.fastapi import OAuth2AuthorizeCallback
from httpx_oauth.clients.github import GitHubOAuth2
from httpx_oauth.clients.google import GoogleOAuth2
from httpx_oauth.clients.facebook import FacebookOAuth2


router = APIRouter()

router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

# JWT backend authentication
router.include_router(
    fastapi_users.get_auth_router(jwt_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

# Cookie backend authentication
router.include_router(
    fastapi_users.get_auth_router(cookie_backend),
    prefix="/auth/cookie",
    tags=["auth"],
)

# Register user router
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

# Reset user password router
router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)

# Email verification routes
router.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"]
)

# Generic OAuth
if settings.OAUTH_ENABLED:
    oauth_client = OAuth2("CLIENT_ID", "CLIENT_SECRET", "AUTHORIZE_ENDPOINT", "ACCESS_TOKEN_ENDPOINT")

# Facebook OAuth
if settings.OAUTH_FACEBOOK:
    facebook_oauth_client = FacebookOAuth2(settings.FACEBOOK_CLIENT_ID, settings.FACEBOOK_CLIENT_SECRET)

    router.include_router(
        fastapi_users.get_oauth_router(
            facebook_oauth_client, jwt_backend, facebook_oauth_client.client_secret, redirect_url=f"{settings.REDIRECT_URL}?provider=facebook"),
        prefix="/auth/facebook",
        tags=["auth"]
    )

# Github OAuth
if settings.OAUTH_GITHUB:
    github_oauth_client = GitHubOAuth2(settings.GITHUB_CLIENT_ID, settings.GITHUB_CLIENT_SECRET)

    router.include_router(
        fastapi_users.get_oauth_router(
            github_oauth_client, jwt_backend, github_oauth_client.client_secret, redirect_url=f"{settings.REDIRECT_URL}?provider=github"),
        prefix="/auth/github",
        tags=["auth"]
    )

# Google OAuth
if settings.OAUTH_GOOGLE:
    google_oauth_client = GoogleOAuth2(settings.GOOGLE_CLIENT_ID, settings.GOOGLE_CLIENT_SECRET)

    router.include_router(
        fastapi_users.get_oauth_router( google_oauth_client, jwt_backend, google_oauth_client.client_secret, redirect_url=f"{settings.REDIRECT_URL}?provider=google"),
        prefix="/auth/google",
        tags=["auth"]
    )

@router.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}
