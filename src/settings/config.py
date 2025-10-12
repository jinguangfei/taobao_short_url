import os
import typing
import json
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="",
        validate_assignment=True,
        env_file='.env',
        env_file_encoding='utf-8',
        extra='allow'
    )
    
    # 基础配置
    VERSION: str = "1.0.0"
    APP_TITLE: str = "FastAPI Boilerplate"
    PROJECT_NAME: str = "fastapi-boilerplate"
    APP_DESCRIPTION: str = "FastAPI Boilerplate"

    # CORS配置
    CORS_ORIGINS: typing.List[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: typing.List[str] = ["*"]
    CORS_ALLOW_HEADERS: typing.List[str] = ["*"]

    DEBUG: bool = True

    # 路径配置
    PROJECT_ROOT: str = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    BASE_DIR: str = os.path.abspath(os.path.join(PROJECT_ROOT, os.pardir))
    LOGS_ROOT: str = os.path.join(BASE_DIR, "app/logs")

    # JWT配置
    SECRET_KEY: str = "your-secret-key-here-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30

    # 数据库配置
    @property
    def TORTOISE_ORM(self) -> dict:
        connections = {
            "postgres": {
                "engine": "tortoise.backends.asyncpg",
                "credentials": {
                    "host": "47.94.223.86",
                    "port": 5002,
                    "user": "dcx",
                    "password": "psql@dcx1239",
                    "database": "dcx_admin",
                    "server_settings": {
                        "timezone": "Asia/Shanghai",
                        "TimeZone": "Asia/Shanghai"
                    }
                }
            },
        }
        
        return {
            "connections": connections,
            "apps": {
                "models": {
                    "models": [
                        "aerich.models",
                        "src.admin.models", 
                        "src.account.info.models",
                        "src.account.cost.models",
                        "src.gateway.sync.base.models",
                        "src.gateway.sync.user.models",
                        "src.gateway.sync.call.models",
                        "src.api.tb_cookie.models", 
                    ],
                    "default_connection": "postgres",
                },
            },
            "use_tz": False,
            "timezone": "Asia/Shanghai",
        }

    DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"

    # Redis配置
    REDIS_HOST: str = "47.94.223.86"
    REDIS_PORT: int = 5003
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = "redis@dcx1239"
    REDIS_MAX_CONNECTIONS: int = 100
    REDIS_SECRET_KEY: str = "dcx"

    REDIS_API_TOKEN_LIMIT_KEY: str = "api_token_limit"


settings = Settings()
if __name__ == "__main__":
    print(settings.TORTOISE_ORM)