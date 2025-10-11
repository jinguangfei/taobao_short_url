from fastapi import APIRouter

from src.core.dependency import DependPermisson, DependUserQuery

from .info.router import router as info_router
from .cost.router import router as cost_router

router = APIRouter(prefix="/account", tags=["账户"])

router.include_router(info_router, prefix="/info", dependencies=[DependPermisson, DependUserQuery])
router.include_router(cost_router, prefix="/cost", dependencies=[DependPermisson, DependUserQuery])

__all__ = ["router"]
