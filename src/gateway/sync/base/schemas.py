from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

from ..enums import SyncAPIMethod

class SyncAPICreate(BaseModel):
    name: str = Field(max_length=32, description="名称")
    host: str = Field(max_length=128, description="主机")
    path: Optional[str] = Field(default="/", max_length=128, description="路径")
    method: Optional[SyncAPIMethod] = Field(default=SyncAPIMethod.GET, description="方法")
    allow_query_params: Optional[List[str]] = Field(default=[], description="允许的查询参数")
    allow_headers: Optional[List[str]] = Field(default=[], description="允许的请求头")
    main_params: Optional[List[str]] = Field(default=[], description="主参数")
    white_list: Optional[List[str]] = Field(default=[], description="白名单")

class SyncAPIUpdate(BaseModel):
    id: int = Field(description="ID")
    name: Optional[str] = Field(None, max_length=32, description="名称")
    host: Optional[str] = Field(None, max_length=128, description="主机")
    path: Optional[str] = Field(None, max_length=128, description="路径")
    method: Optional[SyncAPIMethod] = Field(None, description="方法")
    allow_query_params: Optional[List[str]] = Field(default=None, description="允许的查询参数")
    allow_headers: Optional[List[str]] = Field(default=None, description="允许的请求头")
    main_params: Optional[List[str]] = Field(default=None, description="主参数")
    white_list: Optional[List[str]] = Field(default=None, description="白名单")