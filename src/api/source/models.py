from tortoise import fields
from src.core.models import BaseModel

class Source(BaseModel):
    name = fields.CharField(max_length=32, index=True, description="名称")
    uniq_id = fields.CharField(max_length=32, index=True, description="唯一ID")
    value = fields.TextField(description="value")
    init_t = fields.IntField(index=True,description="初始化时间戳")
    use_t = fields.IntField(index=True,description="使用时间戳")
    status = fields.IntField(default=1,index=True, description="状态")

    class Meta:
        table = "source"
        description = "资源表"
        unique_together = (("name", "uniq_id"),)