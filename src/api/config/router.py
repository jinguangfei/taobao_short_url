import json
from datetime import datetime
from fastapi import APIRouter, Query, HTTPException, Body
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from src.core.ctx import CTX_USER_ID, CTX_Q
from src.core.bgtask import BgTasks
from typing import Dict, Any
from .task import config_task
from .check import check_body
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
    item_id: str = Query(..., max_length=30,description="商品ID"),
    timeout: int = Query(10, description="超时时间"),
):
    if not item_id.isdigit():
        return json.dumps({"statusCode": 400, "result_dict": {"flag": "error", "recv_dict": "商品ID必须是数字"}},ensure_ascii=False)
    url = f"https://main.m.taobao.com/app/ltao-fe/we-detail/home.html?id={item_id}"
    config_task.add_task(url)
    result = await config_task.get_result(url, timeout)
    body, body_info = check_body(result)
    # 如果成功 20秒后删除结果
    if result and body_info not in CONFIG_DATA["break_flag"]:
        await BgTasks.add_task(config_task.delete_result, url, 20)
    else:
        await BgTasks.add_task(config_task.delete_result, url, 0)
    return_dict = {'statusCode': 200, 'result_dict': {"flag":body_info,"recv_dict":body}}
    return json.dumps(return_dict,ensure_ascii=False)

class GetTaskRequest(BaseModel):
    config : Dict[str, Any]
# 获取任务并完成任务
@router.post("/get_task", summary="获取任务")
async def get_task(
):
    return config_task.get_task()

@router.post("/over_task", summary="完成任务")
def over_task(
    url: str = Body(..., description="URL"),
    result: str = Body(..., description="结果"),
    real_url: str = Body(..., description="真实URL"),
    ua: str = Body(..., description="UA"),
    cookie: str = Body(..., description="Cookie"),
):
    item_id = url.split("=")[-1]
    if item_id in real_url:
        body, body_info = check_body(result) 
        info = ""
        config_task.over_task(url, body)
        if body_info == "slide":
            slide_url : str = json.loads(body).get("data",{}).get("url","")

            print(cookie)
            info = get_x5sec(slide_url, ua, cookie)
        return {"flag":body_info,"info":info}
    else:
        return "not_match"