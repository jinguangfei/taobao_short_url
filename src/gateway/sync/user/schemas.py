from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class UserSyncAPICreate(BaseModel):
    user_id: int = Field(description="用户ID")
    sync_api_id: int = Field(description="同步APIID")
    capacity: int = Field(default=1, description="容量")
    rate: float = Field(default=1, description="速率")
    is_active: bool = Field(default=True, description="是否有效")
    timeout: int = Field(default=10, description="超时时间")
    unit_price: float = Field(default=0.1, description="单价")

class UserSyncAPIUpdate(BaseModel):
    id: int = Field(description="ID")
    capacity: Optional[int] = Field(None, description="容量")
    rate: Optional[float] = Field(None, description="速率")
    is_active: Optional[bool] = Field(None, description="是否有效")
    timeout: Optional[int] = Field(None, description="超时时间")
    unit_price: Optional[float] = Field(None, description="单价")