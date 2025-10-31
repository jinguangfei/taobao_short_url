from enum import StrEnum

class ExtFunctionStatus(StrEnum):
    FAIL = "fail"
    SUCCESS = "success"

class ExtFunctionName(StrEnum):
    CRAWL = "crawl"
    SCREEN = "screen"
    REMOVE = "remove"