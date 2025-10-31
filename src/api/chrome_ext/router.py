import json
from datetime import datetime
from fastapi import APIRouter, Query, HTTPException, Body
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from src.core.bgtask import BgTasks
from typing import Dict, Any

from src.core.ctx import CTX_USER_ID
from src.core.dependency import DependAuth
from src.admin.schemas import Success, SuccessExtra, Fail
from .servcie import ChromeExtService, APIInfo
from .config import TaskType
chrome_ext_service = ChromeExtService()
from ..x5sec.service import get_x5sec

router = APIRouter()

@router.get("/", summary="",response_class=PlainTextResponse)
async def item(
    # item_id 都是数字,限制长度为30
    item_id: str = Query(..., regex=r"^\d+$",max_length=30,description="商品ID"),
    timeout: int = Query(10, description="超时时间"),
    task_type: TaskType = Query(TaskType.LT_TAOBAO, description="任务类型"),
    batch: str = Query(None, description="日期"),
):
    if batch:
        task_info = chrome_ext_service.api_info.TaskInfo(item_id=item_id, timeout=timeout, task_type=task_type, batch=batch)
    else:
        task_info = chrome_ext_service.api_info.TaskInfo(item_id=item_id, timeout=timeout, task_type=task_type)
    print(task_info.uniq_id)
    body, body_info = await chrome_ext_service.crawl(task_info)
    return_dict = {'statusCode': 200, 'result_dict': {"flag":body_info,"recv_dict":body}}
    return json.dumps(return_dict,ensure_ascii=False)

class GetTaskRequest(BaseModel):
    config : Dict[str, Any]
# 获取任务并完成任务
@router.post("/get_task", summary="获取任务",dependencies=[DependAuth])
async def get_task(
    worker_info : APIInfo.WorkerInfo
) -> APIInfo.WorkerTaskInfo | None:
    task_info = await chrome_ext_service.get_task(worker_info)
    return Success(data=task_info.model_dump())

@router.post("/over_task", summary="完成任务",dependencies=[DependAuth])
async def over_task(
    over_task_info : APIInfo.OverTaskInfo
):
    result = await chrome_ext_service.over_task(over_task_info)
    return Success(data=result)