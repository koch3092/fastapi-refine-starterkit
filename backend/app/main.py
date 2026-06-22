import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi_refine import configure_refine
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings


def custom_generate_unique_id(route: APIRoute) -> str:
    """Build a stable OpenAPI operation id that stays unique across aliases."""
    tag = route.tags[0] if route.tags else "default"
    method = next(iter(sorted(route.methods or []))).lower()
    path = (
        route.path_format.strip("/")
        .replace("/", "_")
        .replace("-", "_")
        .replace("{", "")
        .replace("}", "")
    )
    return f"{tag}_{route.name}_{method}_{path}"


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["x-total-count"],
    )

configure_refine(app)
app.include_router(api_router, prefix=settings.API_V1_STR)
