import json
from datetime import datetime
from fastapi import APIRouter, Query, HTTPException, Body
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from src.core.bgtask import BgTasks
from typing import Dict, Any

from .servcie import ChromeExtService, APIInfo
chrome_ext_service = ChromeExtService()
from ..x5sec.service import get_x5sec

router = APIRouter()
CONFIG_DATA = {
        "name": '陶特详情',
        "type": 'network',
        "domain": 'taobao.com',
        "url_whitelist": ['mtop.taobao.ltao.detail.h5.data.get'],
        "url_blacklist": [],
        "body_whitelist": [],
        "body_blacklist": ['FAIL_SYS_TOKEN',],
        "web": True,
        "timeout": 20,
        "break_flag": ["login","deny"]
    }

@router.get("/current", summary="获取当前配置")
async def current(
):
    return CONFIG_DATA

@router.get("/", summary="",response_class=PlainTextResponse)
async def item(
    # item_id 都是数字,限制长度为30
    item_id: str = Query(..., regex=r"^\d+$",max_length=30,description="商品ID"),
    timeout: int = Query(10, description="超时时间"),
):
    task_info = chrome_ext_service.api_info.TaskInfo(item_id=item_id, timeout=timeout)
    body, body_info = await chrome_ext_service.crawl(task_info)
    # 如果成功 20秒后删除结果
    if body and body_info not in CONFIG_DATA["break_flag"]:
        await BgTasks.add_task(chrome_ext_service.task.delete, task_info.uniq_id, 20)
    else:
        await BgTasks.add_task(chrome_ext_service.task.delete, task_info.uniq_id, 0)
    return_dict = {'statusCode': 200, 'result_dict': {"flag":body_info,"recv_dict":body}}
    return json.dumps(return_dict,ensure_ascii=False)

class GetTaskRequest(BaseModel):
    config : Dict[str, Any]
# 获取任务并完成任务
@router.post("/get_task", summary="获取任务")
async def get_task(
    worker_info : APIInfo.WorkerInfo
) -> APIInfo.WorkerTaskInfo | None:
    return chrome_ext_service.get_task(worker_info)

@router.post("/over_task", summary="完成任务")
def over_task(
    over_task_info : APIInfo.OverTaskInfo
):
    return chrome_ext_service.over_task(over_task_info)