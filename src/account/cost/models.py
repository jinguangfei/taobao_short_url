from tortoise import fields
from src.admin.models.base import BaseModel, TimestampMixin
from .enums import CostType

class AccountCost(BaseModel, TimestampMixin):
    user = fields.ForeignKeyField('models.User', description='关联用户')
    item = fields.CharField(max_length=32, index=True, description="消费项目")
    amount = fields.FloatField(description="金额")
    cost_type = fields.CharEnumField(CostType, description="消费类型")  # 充值或消费
    remark = fields.CharField(max_length=255, index=True, description="备注")

    class Meta:
        table = "account_cost"
        description = "消费记录表"