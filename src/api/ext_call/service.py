import json
import base64
from math import e
from typing import Optional
from fastapi import Request
from typing import List, Dict, Any

from src.core.schemas import Fail, Success
from src.core.ctx import CTX_USER_ID

from src.account.cost.controllers import account_cost_controller, AccountCostCreate, CostType
from ..ext.base.controllers import ext_function_controller, ExtFunction
from ..ext.base.schemas import ExtFunctionOut
from ..ext.user.controllers import user_ext_function_controller, UserExtFunction

from src.loger import logger
from .task import task
from .config import WorkerInfo, WorkerTaskInfo, OverTaskInfo
from ..ext_handler.service import url_handler, cookie_handler
from src.api.utils.func import (
    cookie_queue,
    get_taobao_tk,
    parse_cookie_str,
    get_mi_id,
    parse_url,
    build_url,
    get_x5sec,
)
from .check import pc_check_body as check_body

class ExtCallService(object):

    async def call(self, name: str, batch: str, request: Request) -> Optional[Success | Fail]:
        """
        1. 获取功能
        2. 获取主参数
        3. 生成任务id
        4. 添加任务
        5. 获取任务结果
        6. 删除任务
        """
        ext_function = await ext_function_controller.get_by_name(name=name)
        if ext_function is None:
            result = Fail(msg="功能不存在")
        else:
            main_params = ext_function.main_params
            main_params = {k: request.query_params.get(k,"") for k in main_params}
            task_id = json.dumps({
                "name": name,
                "batch": batch,
                "main_params": main_params
            }).replace(" ","")
            timeout = request.query_params.get("timeout", ext_function.timeout)
            _result : Optional[str] = await task.get_result(name, task_id, 1)
            if _result: # 有结果
                result = Success(data=_result)
            else:
                task.add(name, task_id)
                _result : Optional[str] = await task.get_result(name, task_id, timeout)
                if _result is None:
                    result = Fail(msg="任务超时")
                else:
                    result = Success(data=_result)
                await task.delete_task(name, task_id, 0)
        return result

    async def handle_task(self, ext_function : ExtFunction, task_id : str) -> Optional[Success | Fail]:
        """
        1. 获取主参数dict
        2. 如果功能是PC_DETAIL，则需要用main_params_dict中的id去获取商品mid_url
        3. 如果功能是LT_DETAIL，则直接生成url
        """
        # 获取主参数dict
        main_params_dict = json.loads(task_id).get("main_params",{})
        user_id = CTX_USER_ID.get() 
        if ext_function.name == "PC_SCREEN":
            # 需要用main_params_dict中的id去获取商品mid_url
            result_dict = await url_handler.handler(**main_params_dict)
        elif ext_function.name == "PC_DETAIL":
            result_dict = await cookie_handler.handler(user_id=user_id)
            if result_dict.get("cookie"):
                result_dict.update(await url_handler.handler(**main_params_dict))
        elif ext_function.name == "LT_DETAIL":
            result_dict = await cookie_handler.handler(user_id=user_id)
        return result_dict
        

    async def get_task(self, worker_info : WorkerInfo) -> Optional[WorkerTaskInfo]:
        """
        1. 获取用户id
        2. 获取用户插件功能
        3. 获取任务id
        4. 处理任务
        5. 返回任务结果
        """
        user_id = CTX_USER_ID.get()
        user_ext_function_objs : List[UserExtFunction] = await user_ext_function_controller.model.filter(
            user_id=user_id,
            is_active=True
        )
        if len(user_ext_function_objs) == 0: # 该用户没有插件功能
            return Success(msg="没有插件功能")
        for user_ext_function in user_ext_function_objs:
            ext_function : ExtFunction = await user_ext_function.ext_function
            task_id = task.get(ext_function.name)
            if task_id: break
        else: # 没有任务
            return Success(msg="没有任务")
        # 处理任务
        result_dict : Dict[str, Any] = await self.handle_task(ext_function, task_id)
        worker_task_info = WorkerTaskInfo(
            task_id=task_id,
            ext_function=ExtFunctionOut.model_validate(await ext_function.to_dict()),
            **result_dict
        )
        return Success(data=worker_task_info.model_dump())

    async def over_task(self, over_task_info : OverTaskInfo) -> tuple[str, str]:
        # cookie信息
        cookie_str = over_task_info.task_info.cookie.get("cookie","")
        cookie_dict = parse_cookie_str(cookie_str)
        cookie_id = over_task_info.task_info.cookie.get("id")

        # 任务信息
        user_id = CTX_USER_ID.get()
        task_info = over_task_info.task_info
        task_id = task_info.task_id
        item_id = task_info.main_params.get("id")
        body = over_task_info.result.get("body","")

        # user_ext_function信息
        user_ext_function = await user_ext_function_controller.get_by_name(user_id=user_id, name=task_info.ext_function.name)
        if user_ext_function is None:
            return Success(msg="用户插件功能不存在")

        info = ""
        if item_id and item_id in over_task_info.real_url:
            body, body_info = check_body(body)
            over_task_info.result.update({"body":body,"body_info":body_info})
            match body_info:
                case "slide":
                    slide_url : str = json.loads(body).get("data",{}).get("url","")
                    x5sec = await get_x5sec(slide_url, over_task_info.ua, cookie_dict)
                    logger.info(f"get_x5sec {x5sec}")
                    if x5sec:
                        info = x5sec
                        cookie_handler.redis.hset(cookie_handler.x5sec_key, cookie_id, x5sec)
                case "success" | "noitem":
                    task.over(task_info.ext_function.name, task_id, json.dumps(over_task_info.result))
                    await user_ext_function_controller.over(user_ext_function, task_id, body_info, body, 0)
                case "deny":
                    cookie_handler.redis.hdel(cookie_handler.cookie_key, user_id)
                case "login":
                    cookie_handler.redis.hdel(cookie_handler.cookie_key, user_id)
        else:
            body_info = "not_match"
        logger.info(f"over_task user:{user_id} coookie:{cookie_id} {task_id} {body_info}")
        return Success(data={"flag":body_info,"info":info})
service = ExtCallService()