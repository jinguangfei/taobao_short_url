from fastapi import APIRouter, Depends

from src.core.dependency import DependPermisson, DependUserQuery

router = APIRouter(prefix="/sync", tags=["同步网关"])
from .base.router import router as base_router
from .user.router import router as user_router
from .call.router import router as call_router
router.include_router(base_router, prefix="", dependencies=[DependPermisson])
router.include_router(user_router, prefix="/user", dependencies=[DependPermisson, DependUserQuery])
router.include_router(call_router, prefix="/call", dependencies=[DependPermisson, DependUserQuery])

__all__ = ["router", "sync_call_router"]