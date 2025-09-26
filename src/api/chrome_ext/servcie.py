import json
import traceback
from re import I
import requests
from typing import Union, Optional
from pydantic import BaseModel
from curl_cffi.requests import AsyncSession

from src.core.redis_script import redis_pool
from src.core.bgtask import BgTasks
from src.loger import logger

from .task import Task
from .check import check_body
from .config import APIInfo
from ..x5sec.service import get_x5sec
from .zhihai_cookie import MyQueue

class ChromeExtService(object):
    def __init__(self, name : str = "chrome_ext"):
        self.redis = redis_pool
        self.task = Task(name)
        self.logger = logger
        self.api_info = APIInfo
        self.cookie_queue = MyQueue(queue_name="cookie")

    async def crawl(self, task_info : APIInfo.TaskInfo) -> str:
        self.task.add(task_info.uniq_id)
        result = await self.task.get_result(task_info.uniq_id, task_info.timeout)
        body, body_info = check_body(result)
        if body_info in ["login","deny"]:
            self.task.delete(task_info.uniq_id)
        else:
            await BgTasks.add_task(self.task.delete, task_info.uniq_id, 20)

        return body, body_info

    async def get_short_url(self, task_info : APIInfo.TaskInfo, worker_info : APIInfo.WorkerInfo) -> str:
        url = self.api_info.short_url_api
        data = {
            "targetId": task_info.item_id,
            "targetUrlType": task_info.task_type,
            "cookie": worker_info.cookie,
            "proxies": worker_info.proxies,
        }
        flag, short_url = "", ""
        try:
            async with AsyncSession() as s: 
                res = await s.post(url, json=data, timeout=10)
            self.logger.info(f"get_short_url : {res.text}")
            result = res.json().get("result",{})
            short_url = result.get("short_url") if result else ""
            flag = res.json().get("flag")
        except Exception as e:
            logger.error(traceback.format_exc())
        return flag, short_url

    async def get_one_cookie(self, view_name : str = "", add_t : int = 12) -> Optional[str]:
        cookie_info = await self.cookie_queue.get_one_info(view_name=view_name,add_t=add_t)
        if not cookie_info:
            return None
        use_times = cookie_info.get("use_times",0)
        cookie_id = cookie_info.get("id")
        if use_times > 0 and use_times % 20 == 0:
            await self.cookie_queue.wait(cookie_id,60*60,view_name=view_name)
        async def delete_cookie():
            await self.cookie_queue.delete(cookie_id,view_name=view_name)
        return cookie_info.get("cookie"), delete_cookie

    async def prev_task(self, task_info : APIInfo.TaskInfo, worker_info : APIInfo.WorkerInfo) -> Optional[APIInfo.WorkerTaskInfo]:
        cookie_info, short_url = {}, ""
        # 获取cookie
        cookie_info, delete_cookie = await self.get_one_cookie(view_name="chrome_ext",add_t=12)
        # 获取short_url
        if not cookie_info:
            return self.api_info.WorkerTaskInfo(flag="not_have_cookie")
        worker_info.cookie = cookie_info
        flag, short_url = await self.get_short_url(task_info, worker_info)
        if flag in ["login"]:
            await delete_cookie()
        return self.api_info.WorkerTaskInfo(
                task_info=task_info,
                short_url=short_url,
                cookie=worker_info.cookie,
                flag=flag,
                config=self.api_info.CONFIG_DATA
                )

    async def get_task(self, worker_info : APIInfo.WorkerInfo) -> Union[APIInfo.WorkerTaskInfo, None]:
        task_id = self.task.get()
        if not task_id:
            worker_task_info = self.api_info.WorkerTaskInfo(flag="not_have_task")
        else:
            task_info = self.api_info.TaskInfo(item_id=task_id)
            worker_task_info = await self.prev_task(task_info, worker_info)
        self.logger.info(f"get_task : {worker_task_info.flag} {worker_task_info.short_url} {worker_task_info.task_info}")
        return worker_task_info

    def over_task(self, over_task_info : APIInfo.OverTaskInfo) -> tuple[str, str]:
        item_id = over_task_info.task_info.item_id

        info = ""
        if item_id in over_task_info.real_url:
            body, body_info = check_body(over_task_info.result)
            self.task.over(over_task_info.task_info.uniq_id, body)
            if body_info == "slide":
                slide_url : str = json.loads(body).get("data",{}).get("url","")
                x5sec = get_x5sec(slide_url, over_task_info.ua, over_task_info.worker_info.cookie)
                info = x5sec
        else:
            body_info = "not_match"
        self.logger.info(f"over_task : {body_info} {info}")
        return {"flag":body_info,"info":info}

