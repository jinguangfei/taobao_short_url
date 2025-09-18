from fastapi import APIRouter
from .short_url.router import router as short_url_router
from .taobao_tk.router import router as taobao_tk_router


router = APIRouter(tags=["api"],prefix="/api")

router.include_router(short_url_router,prefix="/short_url")
router.include_router(taobao_tk_router,prefix="/taobao_tk")