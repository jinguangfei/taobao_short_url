from fastapi import APIRouter
from .base.router import router as base_router
from .short_url.router import router as short_url_router
from .taobao_tk.router import router as taobao_tk_router
from .x5sec.router import router as x5sec_router
from .damai_cookie.router import router as damai_cookie_router
from .mi_id.router import router as mi_id_router


router = APIRouter(tags=["api"],prefix="/api")

router.include_router(base_router,prefix="/base")
router.include_router(short_url_router,prefix="/short_url")
router.include_router(taobao_tk_router,prefix="/taobao_tk")
router.include_router(x5sec_router,prefix="/x5sec")
router.include_router(damai_cookie_router,prefix="/damai_cookie")
router.include_router(mi_id_router,prefix="/mi_id")