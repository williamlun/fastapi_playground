"""fast api playground"""
import fastapi
from fastapi import status
import routers.demo_service

import uvicorn

app = fastapi.FastAPI()
app.include_router(routers.demo_service.router, tags=["demo"])


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8077, reload=True)
