from fastapi import APIRouter

from src.core.dependency import DependPermisson

from .sync.router import router as sync_router
from .sync.user.router import sync_call_router

router = APIRouter(prefix="/gateway")
router.include_router(sync_router, tags=["同步网关"])
router.include_router(sync_call_router, tags=["同步网关"])

__all__ = ["router"]
