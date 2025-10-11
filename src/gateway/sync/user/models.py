from tortoise import fields
from src.admin.models.base import BaseModel, TimestampMixin

class UserSyncAPI(BaseModel, TimestampMixin):
    user = fields.ForeignKeyField("models.User", on_delete=fields.CASCADE, description="用户")
    sync_api = fields.ForeignKeyField("models.SyncAPI", on_delete=fields.CASCADE, description="同步API")
    # 限速
    capacity = fields.IntField(default=1, description="容量")
    rate = fields.FloatField(default=1, description="速率")
    is_active = fields.BooleanField(default=True, description="是否有效")
    timeout = fields.IntField(default=10, description="超时时间")
    # 计数, 单价
    unit_price = fields.FloatField(description="单价")

    class Meta:
        table = "user_sync_api"
        description = "用户同步API表"
        unique_together = [
            ("user", "sync_api")
        ]