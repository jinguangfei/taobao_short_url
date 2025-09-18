from fastapi import APIRouter
from .config.router import router as config_router

router = APIRouter(tags=["api"],prefix="/api")

router.include_router(config_router,prefix="/config")