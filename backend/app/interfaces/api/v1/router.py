from fastapi import APIRouter

from app.interfaces.api.v1.routers.health import router as health_router


router = APIRouter()

router.include_router(
    health_router,
    prefix="/health",
    tags=["Health"],
)

# Teams

# Players

# Matches

# Predictions

# Statistics

# Authentication

# Administration
