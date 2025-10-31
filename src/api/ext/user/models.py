from tortoise import fields
from src.core.models import BaseModel, TimestampMixin
from src.api.ext.base.models import ExtFunction

class UserExtFunction(BaseModel, TimestampMixin):
    user = fields.ForeignKeyField("models.User", on_delete=fields.CASCADE, description="用户")
    ext_function = fields.ForeignKeyField("models.ExtFunction", on_delete=fields.CASCADE, description="插件功能")
    is_active = fields.BooleanField(default=True, description="是否有效")
    # 计数, 单价
    unit_price = fields.FloatField(description="单价")

    class Meta:
        table = "user_ext_function"
        description = "用户插件功能表"
        unique_together = [
            ("user", "ext_function")
        ]