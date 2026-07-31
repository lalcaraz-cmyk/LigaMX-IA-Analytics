from fastapi import APIRouter

from app.core.config import get_settings
from app.interfaces.api.v1.router import router as v1_router


settings = get_settings()

api_router = APIRouter()

api_router.include_router(
    v1_router,
    prefix=settings.API_V1_PREFIX,
)

# Version 2

# Internal API

# Administration API
