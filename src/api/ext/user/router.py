from typing import Dict, Any
from datetime import datetime
from fastapi import APIRouter, Query, HTTPException, Request, Depends
from tortoise.expressions import Q
from src.admin.schemas import Success, SuccessExtra, Fail
from src.core.ctx import CTX_USER_ID, CTX_Q

from .schemas import UserExtFunctionCreate, UserExtFunctionUpdate
from .controllers import (
    user_ext_function_controller, 
)

router = APIRouter()
@router.get("/list", summary="查看用户插件功能列表")
async def list_user_ext_function(
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    user_name : str = Query(None, description="用户名"),
    ext_function_name : str = Query(None, description="插件功能名称"),
):
    q = CTX_Q.get()
    if user_name is not None:
        q &= Q(user__username__icontains=user_name)
    if ext_function_name is not None:
        q &= Q(ext_function__name__icontains=ext_function_name)

    total, user_ext_function_objs = await user_ext_function_controller.list(page=page, page_size=page_size, search=q, order=["id"])
    # 转换每个对象为字典，并包含外键详情
    data = [await obj.to_dict(fk=True, exclude_fields=["password"]) for obj in user_ext_function_objs]
    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)

@router.post("/create", summary="创建用户插件功能")
async def create_user_sync_api(
    user_ext_function_in: UserExtFunctionCreate,
):
    user_ext_function_obj = await user_ext_function_controller.create(obj_in=user_ext_function_in)
    return Success(data=await user_ext_function_obj.to_dict())

@router.put("/update", summary="更新用户同步API")
async def update_user_ext_function(
    user_ext_function_in: UserExtFunctionUpdate,
):
    # 每个人只能更新自己的, 或者管理员
    q = CTX_Q.get()
    q &= Q(id=user_ext_function_in.id)
    user_ext_function_obj = await user_ext_function_controller.model.filter(q).first()
    if not user_ext_function_obj:
        raise HTTPException(status_code=404, detail="插件功能不存在")
    user_ext_function_obj = await user_ext_function_controller.update(user_ext_function_in.id,obj_in=user_ext_function_in)
    return Success(data=await user_ext_function_obj.to_dict())


@router.delete("/delete", summary="删除用户插件功能")
async def delete_user_ext_function(
    id : int,
):
    await user_ext_function_controller.remove(id)
    return Success(msg="删除成功")


__all__ = ["router"]