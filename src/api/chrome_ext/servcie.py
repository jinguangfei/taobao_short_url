import json
from shutil import which
import traceback
from re import I
import requests
import random
from typing import Union, Optional
from pydantic import BaseModel
from curl_cffi.requests import AsyncSession

from src.core.redis_script import redis_pool
from src.core.bgtask import BgTasks
from src.loger import logger
from src.core.ctx import CTX_USER_ID
from src.account.cost.controllers import account_cost_controller, AccountCostCreate, CostType

from .task import Task
from .check import check_body
from .config import APIInfo, config_dict
from ..x5sec.service import get_x5sec
from .utils import get_mi_id
from .zhihai_cookie import MyQueue

class ChromeExtService(object):
    def __init__(self, name : str = "chrome_ext"):
        self.redis = redis_pool
        self.task = Task(name)
        self.logger = logger
        self.api_info = APIInfo
        self.cookie_queue = MyQueue(queue_name="cookie")
        self.x5sec_key = f"{name}:x5sec"
        self.cookie_key = f"{name}:cookie"

    async def crawl(self, task_info : APIInfo.TaskInfo) -> str:
        result = await self.task.get_result(task_info.uniq_id, 1)
        if not result:
            self.task.add(task_info.uniq_id)
            result = await self.task.get_result(task_info.uniq_id, task_info.timeout)
        body, body_info = check_body(result, task_info.task_type)
        logger.info(f"crawl : {body_info} {len(body)}")
        return body, body_info

    async def get_short_url(self, task_info : APIInfo.TaskInfo, cookie_info : dict) -> str:
        url = self.api_info.short_url_api
        data = {
            "targetId": task_info.item_id,
            "targetUrlType": task_info.task_type,
            "cookie": cookie_info.get("cookie"),
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

    async def get_one_cookie(self, user_id : int, view_name : str = "", add_t : int = 12) -> Optional[dict]:
        cookie_info = self.redis.hget(self.cookie_key, user_id)
        if cookie_info:
            cookie_info = json.loads(cookie_info)
        else:
            cookie_info = await self.cookie_queue.get_one_info(view_name=view_name,add_t=add_t)
            if cookie_info:
                self.redis.hset(self.cookie_key, user_id, json.dumps(cookie_info))
                cookie_id = cookie_info.get("id")
                await self.cookie_queue.delete(cookie_id,view_name=view_name)
        return cookie_info

    async def prev_task_short_url(self, task_info : APIInfo.TaskInfo, worker_info : APIInfo.WorkerInfo) -> Optional[APIInfo.WorkerTaskInfo]:
        cookie_info, short_url = {}, ""
        user_id = CTX_USER_ID.get()
        # 获取cookie
        cookie_info = await self.get_one_cookie(user_id,view_name="chrome_ext",add_t=12)
        # 获取short_url
        if not cookie_info:
            flag = "not_have_cookie"
        else:
            flag, short_url = await self.get_short_url(task_info, cookie_info)
            if flag in ["login"]:
                self.redis.hdel(self.cookie_key, user_id)
                flag = "login"
            elif flag in [""]:
                flag = "empty"
            else:
                flag = "success"
        cookie_id = cookie_info.get("id") if cookie_info else ""
        self.logger.info(f"prev_task_short_url user:{user_id} cookie_id:{cookie_id} flag:{flag}")
        if flag in ["not_have_cookie","empty","login"]:
            self.task.add(task_info.uniq_id)
            return self.api_info.WorkerTaskInfo(flag=flag)
        else:
            x5sec = self.redis.hget(self.x5sec_key, cookie_info.get("id"))
            if x5sec:
                cookie_info["cookie"] = f"{cookie_info['cookie']};x5sec={x5sec.decode()}"

            return self.api_info.WorkerTaskInfo(
                    task_info=task_info,
                    short_url=short_url,
                    cookie=cookie_info,
                    flag=flag,
                    config=config_dict[task_info.task_type]
                    )

    async def prev_task_mi_id(self, task_info : APIInfo.TaskInfo, worker_info : APIInfo.WorkerInfo) -> Optional[APIInfo.WorkerTaskInfo]:
        cookie_info = {}
        user_id = CTX_USER_ID.get()
        # 获取cookie
        cookie_info = await self.get_one_cookie(user_id,view_name="chrome_ext",add_t=12)
        # 获取short_url
        if not cookie_info:
            flag = "not_have_cookie"
        else:
            mi_id = await get_mi_id()
            flag = "not_have_mi_id" if not mi_id else "success"
        cookie_id = cookie_info.get("id") if cookie_info else ""
        self.logger.info(f"prev_task user:{user_id} cookie_id:{cookie_id} flag:{flag}")
        if flag in ["not_have_cookie","not_have_mi_id"]:
            self.task.add(task_info.uniq_id)
            return self.api_info.WorkerTaskInfo(flag=flag)
        else:
            target_url = task_info.base_url.format(item_id=task_info.item_id, mi_id=mi_id)
            x5sec = self.redis.hget(self.x5sec_key, cookie_info.get("id"))
            if x5sec:
                cookie_info["cookie"] = f"{cookie_info['cookie']};x5sec={x5sec.decode()}"
            return self.api_info.WorkerTaskInfo(
                    task_info=task_info,
                    short_url=target_url,
                    cookie=cookie_info,
                    flag="success",
                    config=config_dict[task_info.task_type]
                    )

    async def prev_task(self, task_info : APIInfo.TaskInfo, worker_info : APIInfo.WorkerInfo) -> Optional[APIInfo.WorkerTaskInfo]:
        #return await self.prev_task_mi_id(task_info, worker_info)
        return await self.prev_task_short_url(task_info, worker_info)

    async def get_task(self, worker_info : APIInfo.WorkerInfo) -> Union[APIInfo.WorkerTaskInfo, None]:
        task_id = self.task.get()
        user_id = CTX_USER_ID.get()
        if not task_id:
            worker_task_info = self.api_info.WorkerTaskInfo(flag="not_have_task")
        else:
            task_info = self.api_info.TaskInfo.gen_by_uniq_id(task_id)
            worker_task_info = await self.prev_task(task_info, worker_info)
        self.logger.info(f"get_task user_id:{user_id} task:{task_id} url:{worker_task_info.short_url}")
        return worker_task_info

    def _parse_cookie_str(self, cookie_str : str) -> dict:
        cookie_dict = {i.split("=")[0]:i.split("=",1)[1] for i in cookie_str.replace("; ",";").split(";") if len(i.split("="))>1}
        return cookie_dict

    async def over_task(self, over_task_info : APIInfo.OverTaskInfo) -> tuple[str, str]:
        item_id = over_task_info.task_info.item_id
        cookie_str = over_task_info.cookie.get("cookie")
        cookie_dict = self._parse_cookie_str(cookie_str)
        cookie_id = over_task_info.cookie.get("id")
        user_id = CTX_USER_ID.get()
        task_info = over_task_info.task_info

        info = ""
        if item_id in over_task_info.real_url:
            body, body_info = check_body(over_task_info.result, over_task_info.task_info.task_type)
            match body_info:
                case "slide":
                    slide_url : str = json.loads(body).get("data",{}).get("url","")
                    x5sec = get_x5sec(slide_url, over_task_info.ua, cookie_dict)
                    if x5sec:
                        self.redis.hset(self.x5sec_key, cookie_id, x5sec)
                case "success" | "noitem":
                    self.task.over(over_task_info.task_info.uniq_id, body)
                    await account_cost_controller.create(AccountCostCreate(
                        user_id=user_id,
                        item=f"chrome_ext",
                        amount=0.1,
                        cost_type=CostType.CREDIT,
                        remark=f"{user_id} {cookie_id} {over_task_info.task_info.uniq_id}"
                    ))
                case "deny":
                    self.redis.hdel(self.cookie_key, user_id)
                case "login":
                    self.redis.hdel(self.cookie_key, user_id)
        else:
            body_info = "not_match"
        self.logger.info(f"over_task user:{user_id} coookie:{cookie_id} {task_info.uniq_id} {body_info}")
        return {"flag":body_info,"info":info}

