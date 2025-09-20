import json
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Query, HTTPException, Body
from fastapi.responses import PlainTextResponse


from .service import get_x5sec, parse_cookie_str
from .config import APIInfo

router = APIRouter()
@router.post("/", summary="获取x5sec",response_class=PlainTextResponse)
def current(
    params: APIInfo.Params = Body(..., description="参数"),
):
    cookie_dict = parse_cookie_str(params.cookie_str)
    if params.cookies:
        cookie_dict.update(params.cookies)
    x5sec = get_x5sec(params.slide_url, params.ua, cookie_dict, params.proxies, params.body)
    return x5sec