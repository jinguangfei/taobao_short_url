from tortoise import fields
from src.core.models import BaseModel, TimestampMixin

class ExtFunction(BaseModel, TimestampMixin):
    name = fields.CharField(max_length=64, index=True, unique=True, description="功能名称")
    type = fields.CharField(max_length=64, index=True, description="功能类型")
    domain = fields.CharField(max_length=128, index=True, description="域名")
    url_whitelist = fields.JSONField(default=[], description="URL白名单")
    url_blacklist = fields.JSONField(default=[], description="URL黑名单")
    body_whitelist = fields.JSONField(default=[], description="Body白名单")
    body_blacklist = fields.JSONField(default=[], description="Body黑名单")
    remove_selectors = fields.JSONField(default=[], description="移除选择器")
    function = fields.JSONField(default=[], description="功能")
    timeout = fields.IntField(default=10, description="超时时间")
    break_flag = fields.JSONField(default=[], description="中断标志")
    url_template = fields.CharField(max_length=256, null=True, description="URL模板")
    main_params = fields.JSONField(default=[], null=True, description="主参数")

    class Meta:
        table = "ext_function"
        description = "插件功能表"