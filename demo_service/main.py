"""fast api playground"""
import fastapi
from fastapi import status
import routers.demo_service

import uvicorn
from fastapi.middleware.cors import CORSMiddleware


origins = [
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:3000",
]


app = fastapi.FastAPI()
app.include_router(routers.demo_service.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8077, reload=True)
