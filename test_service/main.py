"""fast api playground"""
import fastapi
from fastapi import status
import routers.demo_service
import keycloak_schema

import uvicorn

app = fastapi.FastAPI()
app.include_router(routers.demo_service.router)


def main():
    uvicorn.run("main:app", host="127.0.0.1", port=8077, reload=True)


def test():
    mycoustomer = keycloak_schema.Customer(name="on9 son")
    print(mycoustomer)


if __name__ == "__main__":
    # main()
    test()
