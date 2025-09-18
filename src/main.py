

import sys
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Query, Path
from fastapi.staticfiles import StaticFiles

from starlette.middleware.gzip import GZipMiddleware
app =  FastAPI()

from src.api.router import router as api_router
from src.core.middlewares import BackGroundTaskMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(BackGroundTaskMiddleware)
app.include_router(api_router)



if __name__ == "__main__":
    port = int(sys.argv[1])
    uvicorn.run(app, host="127.0.0.1", port=port)
    pass