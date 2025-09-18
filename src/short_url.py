# 创建文件：test_app.py
import uvicorn
from fastapi import FastAPI
from src.api.short_url.router import router

app = FastAPI(title="Short URL Test")
app.include_router(router, prefix="/api/short_url")

uvicorn.run(app, host="0.0.0.0", port=8000)