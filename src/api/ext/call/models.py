from tortoise import fields
from src.admin.models.base import BaseModel, TimestampMixin
from ..enums import ExtFunctionStatus

class ExtFunctionCall(BaseModel, TimestampMixin):
    user = fields.ForeignKeyField("models.User", on_delete=fields.CASCADE, description="用户")
    ext_function_name = fields.CharField(max_length=64, index=True, description="插件功能名称")
    call_time = fields.FloatField(description="耗时")
    response_size = fields.IntField(description="响应大小")
    status = fields.CharEnumField(ExtFunctionStatus, description="状态")
    main_key = fields.CharField(max_length=128, index=True, description="主参数")
    
    class Meta:
        table = "ext_function_call"
        description = "插件功能调用表"