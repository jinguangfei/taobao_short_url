from fastapi import APIRouter
from .chrome_ext.router import router as chrome_ext_router

router = APIRouter(tags=["api"],prefix="/api")

router.include_router(chrome_ext_router,prefix="/chrome_ext")