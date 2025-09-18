import contextvars
from tortoise.expressions import Q
from starlette.background import BackgroundTasks

CTX_USER_ID: contextvars.ContextVar[int] = contextvars.ContextVar("user_id", default=0)
CTX_BG_TASKS: contextvars.ContextVar[BackgroundTasks] = contextvars.ContextVar("bg_task", default=None)
CTX_TOKEN: contextvars.ContextVar[str] = contextvars.ContextVar("token", default=None)
CTX_Q: contextvars.ContextVar[Q] = contextvars.ContextVar("q", default=None)