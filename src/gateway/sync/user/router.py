from typing import Dict, Any
from datetime import datetime
from fastapi import APIRouter, Query, HTTPException, Request, Depends
from tortoise.expressions import Q
from src.admin.schemas import Success, SuccessExtra, Fail
from src.core.ctx import CTX_USER_ID, CTX_Q

from .schemas import UserSyncAPICreate, UserSyncAPIUpdate
from .controllers import (
    user_sync_api_controller, 
    UserSyncAPI,
)
from ..enums import SyncAPIStatus

from ..dependency import SyncTokenControl

router = APIRouter()
@router.get("/list", summary="查看用户同步API列表")
async def list_user_sync_api(
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    user_name : str = Query(None, description="用户名"),
    sync_api_name : str = Query(None, description="同步API名称"),
):
    q = CTX_Q.get()
    if user_name is not None:
        q &= Q(user__username__icontains=user_name)
    if sync_api_name is not None:
        q &= Q(sync_api__name__icontains=sync_api_name)

    total, user_sync_api_objs = await user_sync_api_controller.list(page=page, page_size=page_size, search=q, order=["id"])
    # 转换每个对象为字典，并包含外键详情
    data = [await obj.to_dict(fk=True, exclude_fields=["password"]) for obj in user_sync_api_objs]
    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)

@router.post("/create", summary="创建用户同步API")
async def create_user_sync_api(
    user_sync_api_in: UserSyncAPICreate,
):
    user_sync_api_obj = await user_sync_api_controller.create(obj_in=user_sync_api_in)
    return Success(data=await user_sync_api_obj.to_dict())

@router.put("/update", summary="更新用户同步API")
async def update_user_sync_api(
    user_sync_api_in: UserSyncAPIUpdate,
):
    # 每个人只能更新自己的, 或者管理员
    q = CTX_Q.get()
    q &= Q(id=user_sync_api_in.id)
    user_sync_api_obj = await user_sync_api_controller.model.filter(q).first()
    if not user_sync_api_obj:
        raise HTTPException(status_code=404, detail="同步API不存在")
    user_sync_api_obj = await user_sync_api_controller.update(user_sync_api_in.id,obj_in=user_sync_api_in)
    return Success(data=await user_sync_api_obj.to_dict())


@router.delete("/delete", summary="删除用户同步API")
async def delete_user_sync_api(
    id : int,
):
    await user_sync_api_controller.remove(id)
    return Success(msg="删除成功")

sync_call_router = APIRouter()
@sync_call_router.get("/sync_call", summary="Token API 调用")
async def call_sync_gateway(
    request: Request,
    user_sync_api: UserSyncAPI = Depends(SyncTokenControl.validate_token)
):
    flag, body = await user_sync_api_controller.call(user_sync_api, request)
    if flag == SyncAPIStatus.SUCCESS:
        return Success(msg="调用成功", data=body)
    else:
        return Fail(msg="调用失败", data=body)

__all__ = ["router", "sync_call_router"]