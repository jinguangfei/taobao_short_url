from enum import Enum


class StrEnum(str, Enum):
    """字符串枚举的兼容实现，适用于 Python < 3.11"""
    def _generate_next_value_(name, start, count, last_values):
        return name

class ShortTargetUrlType(StrEnum):
    TAOBAO = "TAOBAO"
    LT_TAOBAO = "LT_TAOBAO"
    M_TAOBAO = "M_TAOBAO"