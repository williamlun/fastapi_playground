"""fast api playground"""
import fastapi
from fastapi import status
import routers.a_services
import env
import exceptions

import uvicorn

app = fastapi.FastAPI()
app.include_router(routers.a_services.router, tags=["a_service"], prefix="/a/v1")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8077)
