from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class UserExtFunctionCreate(BaseModel):
    user_id: int = Field(description="用户ID")
    ext_function_id: int = Field(description="插件功能ID")
    unit_price: float = Field(default=0.1, description="单价")
    is_active: bool = Field(default=True, description="是否有效")

class UserExtFunctionUpdate(BaseModel):
    id: int = Field(description="ID")
    is_active: Optional[bool] = Field(None, description="是否有效")
    unit_price: Optional[float] = Field(None, description="单价")