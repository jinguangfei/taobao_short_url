from fastapi import APIRouter
from .ext.router import router as ext_router
from .ext_handler.router import router as ext_handler_router
from .ext_call.router import router as ext_call_router
from src.core.dependency import DependPermisson, DependUserQuery

router = APIRouter(prefix="/api")

router.include_router(ext_router,prefix="/ext",tags=["插件功能"],dependencies=[DependPermisson, DependUserQuery])
router.include_router(ext_call_router,prefix="/ext_call",tags=["插件调用"])
router.include_router(ext_handler_router,prefix="/ext_handler",tags=["处理函数"],dependencies=[DependPermisson, DependUserQuery])