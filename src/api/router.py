from fastapi import APIRouter
from .config.router import router as config_router

router = APIRouter(tags=["config"],prefix="/config")

router.include_router(config_router)