from typing import Dict, Any
from datetime import datetime
from fastapi import APIRouter, Query, HTTPException, Request, Depends
from tortoise.expressions import Q
from src.admin.schemas import Success, SuccessExtra, Fail
from src.core.ctx import CTX_USER_ID, CTX_Q

from .schemas import ExtFunctionCreate, ExtFunctionUpdate
from .controllers import (
    ext_function_controller, 
)

router = APIRouter()
@router.get("/list", summary="查看同步API列表")
async def list_ext_function(
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    name : str = Query(None, description="名称"),
):
    q = Q()
    if name is not None:
        q &= Q(name__icontains=name)
    total, ext_function_objs = await ext_function_controller.list(page=page, page_size=page_size, search=q, order=["id"])
    data = [await obj.to_dict() for obj in ext_function_objs]
    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)

@router.get("/get", summary="获取同步API")
async def get_ext_function(
    name: str = Query(..., description="名称"),
):
    ext_function_obj = await ext_function_controller.get_by_name(name=name)
    if ext_function_obj is None:
        return Fail(msg="功能不存在")
    return Success(data=await ext_function_obj.to_dict())

@router.post("/create", summary="创建同步API")
async def create_sync_api(
    ext_function_in: ExtFunctionCreate,
):
    ext_function_obj = await ext_function_controller.create(obj_in=ext_function_in)
    return Success(data=await ext_function_obj.to_dict())

@router.put("/update", summary="更新同步API")
async def update_ext_function(
    ext_function_in: ExtFunctionUpdate,
):
    ext_function_obj = await ext_function_controller.update(ext_function_in.id,obj_in=ext_function_in)
    return Success(data=await ext_function_obj.to_dict())

@router.delete("/delete", summary="删除同步API")
async def delete_sync_api(
    id : int,
):
    await ext_function_controller.remove(id)
    return Success(msg="删除成功")