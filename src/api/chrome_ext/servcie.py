import json
import traceback
from re import I
import requests
from typing import Union
from pydantic import BaseModel
from src.core.redis_script import redis_pool
from src.core.bgtask import BgTasks
from src.loger import logger

from .task import Task
from .check import check_body
from .config import APIInfo
from ..x5sec.service import get_x5sec

class ChromeExtService(object):
    def __init__(self, name : str = "chrome_ext"):
        self.redis = redis_pool
        self.task = Task(name)
        self.logger = logger
        self.api_info = APIInfo

    async def crawl(self, task_info : APIInfo.TaskInfo) -> str:
        self.task.add(task_info.uniq_id)
        result = await self.task.get_result(task_info.uniq_id, task_info.timeout)
        body, body_info = check_body(result)
        if body_info in ["login","deny"]:
            self.task.delete(task_info.uniq_id)
        else:
            await BgTasks.add_task(self.task.delete, task_info.uniq_id, 20)

        return body, body_info

    def get_short_url(self, task_info : APIInfo.TaskInfo, worker_info : APIInfo.WorkerInfo) -> str:
        url = self.api_info.short_url_api
        data = {
            "targetId": task_info.item_id,
            "targetUrlType": task_info.task_type,
            "cookie": worker_info.cookie,
            "proxies": worker_info.proxies,
        }
        flag, short_url = "", ""
        try:
            res = requests.post(url, json=data, timeout=10)
            self.logger.info(f"get_short_url : {res.text}")
            result = res.json().get("result",{})
            short_url = result.get("short_url") if result else ""
            flag = res.json().get("flag")
        except Exception as e:
            logger.error(traceback.format_exc())
        return flag, short_url

    def get_task(self, worker_info : APIInfo.WorkerInfo) -> Union[APIInfo.WorkerTaskInfo, None]:
        task_id = self.task.get()
        if task_id:
            task_info : APIInfo.TaskInfo = self.api_info.TaskInfo.gen_by_uniq_id(task_id)
            flag, short_url = self.get_short_url(task_info, worker_info)
        else:
            task_info = None
            flag, short_url = "not_have_task", ""
        self.logger.info(f"get_task : {flag} {short_url} {task_info}")
        return self.api_info.WorkerTaskInfo(
                task_info=task_info,
                short_url=short_url,
                flag=flag
                )

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

