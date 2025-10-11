from tortoise import fields
from src.admin.models.base import BaseModel, TimestampMixin
from ..enums import SyncAPIMethod

class SyncAPI(BaseModel, TimestampMixin):
    name = fields.CharField(max_length=32, unique=True, index=True, description="名称")
    host = fields.CharField(max_length=128, description="主机")
    method = fields.CharEnumField(SyncAPIMethod, description="方法")
    path = fields.CharField(max_length=128, description="路径")
    allow_query_params = fields.JSONField(default=[], description="允许的查询参数")
    allow_headers = fields.JSONField(default=[], description="允许的请求头")
    main_params = fields.JSONField(default=[], description="主参数")
    white_list = fields.JSONField(default=[], description="白名单")

    class Meta:
        table = "sync_api"
        description = "同步API表"