import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, Query, HTTPException, Body, Path
from tortoise.expressions import Q

from src.loger import logger
from src.core.schemas import SuccessExtra, Fail, Success
from .service import source_controller

router = APIRouter()


@router.get("/", summary="获取可用资源")
async def get_available_resource(
    name: str = Query(..., description="资源名称"),
    add_t: int = Query(6, description="资源冷却时间（秒）"),
    expire_time: int = Query(56, description="资源过期时间（秒）"),
):
    """
    获取一个可用的资源
    - name: 资源名称（如 cookie, token 等）
    - add_t: 使用后的冷却时间，默认 6 秒
    - expire_time: 资源过期时间，默认 24 小时
    """
    resource = await source_controller.get_available_resource(
            name=name,
            add_t=add_t,
            expire_time=expire_time
        )
    data = await resource.to_dict() if resource else None
    return Success(
        data=data
    )

@router.get("/list", summary="查看资源")
async def list_resource(
    id: int = Query(None, description="ID"),
    name: str = Query(None, description="资源名称"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(100, description="每页数量"),
    status: int = Query(None, description="状态"),
    expire_time: int = Query(None, description="过期时间"),
    order: list = Query([], description="排序"),
):
    q = Q()
    if id is not None:
        q &= Q(id=id)
    if name:
        q &= Q(name=name)
    if status is not None:
        q &= Q(status=status)
    if expire_time is not None:
        q &= Q(init_t__lt=int(time.time()) - expire_time)
    
    total, resources = await source_controller.list(page=page, page_size=page_size, search=q, order=order)
    data = [await obj.to_dict() for obj in resources]
    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)

@router.delete("/", summary="删除资源")
async def delete_resource(
    name: str = Query(..., description="资源名称"),
):
    q = Q(name=name)
    await source_controller.model.filter(q).delete()
    return Success(
        data=None
    )

@router.post("/wait", summary="等待资源")
async def wait_resource(
    id: int = Query(..., description="ID"),
    add_t : int = Query(..., description="添加时间"),
):
    cur_t = int(time.time())
    await source_controller.model.filter(id=id).update(add_t=cur_t + add_t)
    return Success(
        data=None
    )

@router.post("/status", summary="更新资源status")
async def update_resource_status(
    id: int = Query(..., description="ID"),
    status: int = Query(..., description="状态"),
):
    await source_controller.model.filter(id=id).update(status=status)
    return Success(
        data=None
    )