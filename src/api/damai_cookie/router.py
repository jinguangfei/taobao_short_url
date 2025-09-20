import json
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Query, HTTPException, Body
from fastapi.responses import PlainTextResponse


from .service import DamaiCookieService
service = DamaiCookieService()

CONST_KEY = "short_url"

router = APIRouter()
@router.get("/", summary="获取大麦cookie",response_class=PlainTextResponse)
async def current(
):
    return await service.get_cookie()