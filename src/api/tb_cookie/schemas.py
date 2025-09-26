from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class TbCookieCreate(BaseModel):
    cookie: str = Field(..., description="cookie")
    unb: str = Field(..., description="unb")

class TbCookieUpdate(BaseModel):
    pass
