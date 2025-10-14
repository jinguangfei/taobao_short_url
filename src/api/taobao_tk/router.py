import json
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Query, HTTPException, Body
from fastapi.responses import PlainTextResponse


from .service import TaobaoTkService
service = TaobaoTkService()

router = APIRouter()
@router.get("/", summary="获取淘宝tk",response_class=PlainTextResponse)
def current(
):
    return service.get_taobao_tk()