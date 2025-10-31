import json
from datetime import datetime
from fastapi import APIRouter, Query, HTTPException, Body
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from src.core.bgtask import BgTasks
from typing import Dict, Any, Optional
from fastapi import Request

from src.core.ctx import CTX_USER_ID
from src.core.dependency import DependAuth
from src.admin.schemas import Success, SuccessExtra, Fail

from .service import service
from .config import WorkerInfo, WorkerTaskInfo, OverTaskInfo
router = APIRouter()

@router.get("/", summary="call_ext_function",response_class=PlainTextResponse)
async def item(
    request : Request,
    name : str = Query(..., description="功能名称"),
    batch : str = Query(default_factory=lambda: datetime.now().strftime("%Y%m%d"), description="批次"),
):
    result : Optional[Success | Fail] = await service.call(name=name, batch=batch, request=request)
    return result

# chrome_ext获取任务
@router.post("/get_task", summary="chrome_ext获取任务",dependencies=[DependAuth])
async def task(
    worker_info : WorkerInfo
):
    result : Optional[Success | Fail] = await service.get_task(worker_info)
    return result


@router.post("/over_task", summary="chrome_ext完成任务",dependencies=[DependAuth])
async def over_task(
    over_task_info : OverTaskInfo
):
    result : Optional[Success | Fail] = await service.over_task(over_task_info)
    return result