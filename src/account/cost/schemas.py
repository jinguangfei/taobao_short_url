from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

from .enums import CostType

class AccountCostCreate(BaseModel):
    user_id: int = Field(..., description="用户ID")
    item: Optional[str] = Field("", description="消费项目")
    amount: float = Field(..., description="金额")
    cost_type: CostType = Field(..., description="消费类型")
    remark: Optional[str] = Field("", max_length=255, description="备注")

class AccountCostUpdate(BaseModel):
    pass
