from enum import StrEnum

class SyncAPIMethod(StrEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"

class SyncAPIStatus(StrEnum):
    FAIL = "fail"
    SUCCESS = "success"