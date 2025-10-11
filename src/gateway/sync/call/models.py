from tortoise import fields
from src.admin.models.base import BaseModel, TimestampMixin
from ..enums import SyncAPIStatus

class SyncAPICall(BaseModel, TimestampMixin):
    user = fields.ForeignKeyField("models.User", on_delete=fields.CASCADE, description="用户")
    sync_api_name = fields.CharField(max_length=64, index=True, description="同步API名称")
    call_time = fields.FloatField(description="耗时")
    response_size = fields.IntField(description="响应大小")
    status = fields.CharEnumField(SyncAPIStatus, description="状态")
    main_key = fields.CharField(max_length=64, index=True, description="主参数")
    
    class Meta:
        table = "sync_api_call"
        description = "同步API调用表"