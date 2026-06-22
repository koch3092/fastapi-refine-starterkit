from fastapi import APIRouter
from fastapi_refine import refine_error_responses

from app.api.routes import assets, items, login, private, users, utils
from app.core.config import settings

api_router = APIRouter(
    responses=refine_error_responses(  # type: ignore[arg-type]  # FastAPI accepts int response-code keys.
        status_codes=(400, 401, 403, 404, 409, 422, 500, 503)
    ),
)
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(users.owners_router)
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(assets.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
