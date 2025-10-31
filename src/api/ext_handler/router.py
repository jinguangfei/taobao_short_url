import json
from datetime import datetime
from fastapi import APIRouter, Query, HTTPException, Body
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from src.core.bgtask import BgTasks
from typing import Dict, Any, Optional
from fastapi import Request

from .service import cookie_handler, url_handler

router = APIRouter()

@router.get("/cookie", summary="cookie处理")
async def cookie(
    user_id : int,
) -> Dict[str,Any]:
    cookie_info = await cookie_handler.handler(user_id=user_id)
    return {"cookie":cookie_info}

# chrome_ext获取任务
@router.get("/url", summary="url处理")
async def url(
    request : Request,
) -> Dict[str,Any]:
    query_params = request.query_params
    url = await url_handler.handler(**query_params)
    return {"url":url}
    