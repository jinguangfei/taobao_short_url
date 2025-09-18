from fastapi import APIRouter
from .config.router import router as config_router
from .short_url.router import router as short_url_router

router = APIRouter(tags=["api"],prefix="/api")

#router.include_router(config_router,prefix="/config")
router.include_router(short_url_router,prefix="/short_url")