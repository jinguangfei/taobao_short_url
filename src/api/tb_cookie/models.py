from tortoise import fields
from ..models import BaseModel, UUIDModel, TimestampMixin

class TbCookie(BaseModel, TimestampMixin):
    cookie = fields.CharField(max_length=4096)
    unb = fields.CharField(index=True, max_length=32)