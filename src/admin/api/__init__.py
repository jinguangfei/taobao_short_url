from fastapi import APIRouter

from src.core.dependency import DependPermisson

from .apis import apis_router
from .auditlog import auditlog_router
from .base import base_router
from .depts import depts_router
from .menus import menus_router
from .roles import roles_router
from .users import users_router

admin_router = APIRouter()

admin_router.include_router(base_router, prefix="/base")
admin_router.include_router(users_router, prefix="/user", dependencies=[DependPermisson])
admin_router.include_router(roles_router, prefix="/role", dependencies=[DependPermisson])
admin_router.include_router(menus_router, prefix="/menu", dependencies=[DependPermisson])
admin_router.include_router(apis_router, prefix="/api", dependencies=[DependPermisson])
admin_router.include_router(depts_router, prefix="/dept", dependencies=[DependPermisson])
admin_router.include_router(auditlog_router, prefix="/auditlog", dependencies=[DependPermisson])
