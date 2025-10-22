import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class SourceCreate(BaseModel):
    name: str = Field(..., description="名称")
    uniq_id: str = Field(..., description="唯一ID")
    value: str = Field(..., description="value")
    init_t: int = Field(default_factory=lambda: int(time.time()), description="初始化时间戳")
    use_t: int = Field(default=0, description="使用时间戳")

class SourceUpdate(BaseModel):
    use_t: int = Field(default_factory=lambda: int(time.time()), description="使用时间戳")
