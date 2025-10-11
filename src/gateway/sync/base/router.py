from typing import Dict, Any
from datetime import datetime
from fastapi import APIRouter, Query, HTTPException, Request, Depends
from tortoise.expressions import Q
from src.admin.schemas import Success, SuccessExtra, Fail
from src.core.ctx import CTX_USER_ID, CTX_Q

from .schemas import SyncAPICreate, SyncAPIUpdate
from .controllers import (
    sync_api_controller, 
)
from ..enums import SyncAPIStatus

router = APIRouter()
@router.get("/list", summary="查看同步API列表")
async def list_sync_api(
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    name : str = Query(None, description="名称"),
    host : str = Query(None, description="主机"),
):
    q = Q()
    if name is not None:
        q &= Q(name__icontains=name)
    if host is not None:
        q &= Q(host__icontains=host)
    total, sync_api_objs = await sync_api_controller.list(page=page, page_size=page_size, search=q, order=["id"])
    data = [await obj.to_dict() for obj in sync_api_objs]
    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)

@router.post("/create", summary="创建同步API")
async def create_sync_api(
    sync_api_in: SyncAPICreate,
):
    sync_api_obj = await sync_api_controller.create(obj_in=sync_api_in)
    return Success(data=await sync_api_obj.to_dict())

@router.put("/update", summary="更新同步API")
async def update_sync_api(
    sync_api_in: SyncAPIUpdate,
):
    sync_api_obj = await sync_api_controller.update(sync_api_in.id,obj_in=sync_api_in)
    return Success(data=await sync_api_obj.to_dict())

@router.delete("/delete", summary="删除同步API")
async def delete_sync_api(
    id : int,
):
    await sync_api_controller.remove(id)
    return Success(msg="删除成功")

@router.get("/call", summary="调用同步API")
async def call_sync_api(
    request: Request,
    api_name: str = Query(..., description="API名称")
):
    # 获取 SyncAPI 对象
    sync_api_obj = await sync_api_controller.get_by_name(api_name)
    if sync_api_obj is None:
        raise HTTPException(status_code=404, detail="API不存在")

    # 调用 API 并传递过滤后的参数和请求头
    flag, body = await sync_api_controller.call(sync_api_obj, request)
    print(flag)
    if flag == SyncAPIStatus.SUCCESS:
        return Success(msg="调用成功", data=body)
    else:
        return Fail(msg="调用失败", data=body)
