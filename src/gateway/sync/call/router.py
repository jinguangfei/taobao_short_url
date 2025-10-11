from typing import Dict, Any
from datetime import datetime
from fastapi import APIRouter, Query, HTTPException, Request, Depends
from tortoise.expressions import Q
from src.admin.schemas import Success, SuccessExtra, Fail
from src.core.ctx import CTX_USER_ID, CTX_Q

from .schemas import SyncAPICallCreate, SyncAPICallUpdate
from .controllers import (
    sync_api_call_controller, 
)
from ..enums import SyncAPIStatus


router = APIRouter()
@router.get("/list", summary="查看调用记录")
async def list_sync_api_call(
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    user_name : str = Query(None, description="用户名"),
    sync_api_name : str = Query(None, description="同步API名称"),
    main_key : str = Query(None, description="主参数"),
    status : SyncAPIStatus = Query(None, description="状态"),
    start_time: datetime = Query(None, description="开始时间"),
    end_time: datetime = Query(None, description="结束时间"),
):
    q = CTX_Q.get()
    if user_name:
        q &= Q(user__username=user_name)
    if sync_api_name:
        q &= Q(sync_api_name=sync_api_name)
    if main_key:
        q &= Q(main_key__icontains=main_key)
    if status is not None:
        q &= Q(status=status)
    if start_time is not None:
        q &= Q(created_at__gte=start_time)
    if end_time is not None:
        q &= Q(created_at__lte=end_time)

    total, sync_api_call_objs = await sync_api_call_controller.list(page=page, page_size=page_size, search=q, order=["-id"])
    data = [await obj.to_dict(fk=True, exclude_fields=["password","info"]) for obj in sync_api_call_objs]
    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)