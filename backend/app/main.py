from fastapi import FastAPI

from app.core.config import get_settings
from app.interfaces.api.router import api_router


settings = get_settings()

app: FastAPI = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    description="AI-powered analytics and prediction platform for Liga MX.",
    contact={"name": "LigaMX IA Analytics"},
    license_info={"name": "MIT"},
)

app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX,
)

# Middleware

# Exception handlers

# Startup events

# Shutdown events
