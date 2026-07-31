from fastapi import APIRouter, status

from app.core.config import get_settings


router = APIRouter()
settings = get_settings()


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Returns the health status of the API.",
    response_description="API is healthy.",
)
async def health_check() -> dict[str, str]:
    """Return the current health status of the API."""
    return {
        "status": "healthy",
        "service": "LigaMX IA Analytics API",
        "version": settings.VERSION,
    }
