from typing import Optional
from pydantic import BaseModel, Field

class AccountInfoCreate(BaseModel):
    pass

class AccountInfoUpdate(BaseModel):
    id: int = Field(..., description="ID")
    token: Optional[str] = Field(None, description="Token")
    is_active: Optional[bool] = Field(None, description="是否有效")
