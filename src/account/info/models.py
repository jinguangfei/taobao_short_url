from tortoise import fields
from src.admin.models.base import BaseModel, TimestampMixin

class AccountInfo(BaseModel, TimestampMixin):
    user = fields.ForeignKeyField('models.User', description='关联管理员')
    token = fields.CharField(max_length=128, unique=True, description="Token")
    balance = fields.FloatField(default=0.00, description="余额")
    is_active = fields.BooleanField(default=True, description="是否有效")

    class Meta:
        table = "account_info"
        description = "用户信息表"
        unique_together = (("user",),)