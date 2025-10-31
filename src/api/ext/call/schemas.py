from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

from ..enums import ExtFunctionStatus

class ExtFunctionCallCreate(BaseModel):
    user_id: int = Field(description="用户ID")
    ext_function_name: str = Field(max_length=64, description="插件功能名称")
    call_time: float = Field(description="调用时间")
    response_size: int = Field(description="响应大小")
    status: ExtFunctionStatus = Field(description="状态")
    main_key: str = Field(description="主参数")

class ExtFunctionCallUpdate(BaseModel):
    pass