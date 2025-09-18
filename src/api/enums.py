from enum import Enum


class StrEnum(str, Enum):
    """字符串枚举的兼容实现，适用于 Python < 3.11"""
    def _generate_next_value_(name, start, count, last_values):
        return name


class EnumBase(Enum):
    @classmethod
    def get_member_values(cls):
        return [item.value for item in cls._member_map_.values()]

    @classmethod
    def get_member_names(cls):
        return [name for name in cls._member_names_]


class MethodType(StrEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
