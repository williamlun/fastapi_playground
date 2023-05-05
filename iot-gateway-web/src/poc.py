"""small fastapi for import iot gateway config file"""

import fastapi
from fastapi import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import uvicorn
import docker

import os
import secrets
from loguru import logger

app = fastapi.FastAPI()

security = HTTPBasic()

MQTT_PATH = os.getenv("MQTT_PATH", "./config/mqtt.json")
BACKNET_PATH = os.getenv("BACKNET_PATH", "./config/bacnet.json")
TB_GATEWAY_PATH = os.getenv("TB_GATEWAY_PATH", "./config/tb_gateway.yaml")
USERNAME = os.getenv("USERNAME", "admin")
PASSWORD = os.getenv("PASSWORD", "admin")
GATEWAY_IMAGE_NAME = os.getenv("GATEWAY_IMAGE_NAME", "thingsboard/tb-gateway")


def basic_auth(credentials: HTTPBasicCredentials = Depends(security)):
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = USERNAME.encode("utf8")
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = PASSWORD.encode("utf8")
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    if not (is_correct_username and is_correct_password):
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True


@app.get("/probes/healthiness")
def healthiness():
    return


@app.post("/mqtt-config")
async def mqtt_config(
    file: fastapi.UploadFile, correct_auth: bool = Depends(basic_auth)
):
    if not correct_auth:
        return fastapi.HTTPException(status_code=fastapi.status.HTTP_401_UNAUTHORIZED)
    content = file.file.read()
    try:
        with open(MQTT_PATH, "wb") as f:
            f.write(content)
        logger.info(f"mqtt config saved to {MQTT_PATH}")
        return f"mqtt config saved to {MQTT_PATH}"
    except BaseException as e:  # pylint: disable=broad-except
        logger.exception(e)
        raise fastapi.exceptions.HTTPException(status_code=500, detail=e)


@app.post("/bacnet-config")
async def bacnet_config(
    file: fastapi.UploadFile, correct_auth: bool = Depends(basic_auth)
):
    if not correct_auth:
        return fastapi.HTTPException(status_code=fastapi.status.HTTP_401_UNAUTHORIZED)
    content = file.file.read()
    try:
        with open(BACKNET_PATH, "wb") as f:
            f.write(content)
        logger.info(f"bacnet-config saved to {BACKNET_PATH}")
        return f"bacnet-config saved to {BACKNET_PATH}"
    except BaseException as e:  # pylint: disable=broad-except
        logger.exception(e)
        raise fastapi.exceptions.HTTPException(status_code=500, detail=e)


@app.post("/gateway-config")
async def gateway_config(
    file: fastapi.UploadFile, correct_auth: bool = Depends(basic_auth)
):
    if not correct_auth:
        return fastapi.HTTPException(status_code=fastapi.status.HTTP_401_UNAUTHORIZED)
    content = file.file.read()
    try:
        with open(TB_GATEWAY_PATH, "wb") as f:
            f.write(content)
        logger.info(f"gateway config saved to {TB_GATEWAY_PATH}")
        return f"gateway config saved to {TB_GATEWAY_PATH}"
    except BaseException as e:  # pylint: disable=broad-except
        logger.exception(e)
        raise fastapi.exceptions.HTTPException(status_code=500, detail=e)


@app.post("/restart-gateway")
async def restart_gateway(correct_auth: bool = Depends(basic_auth)):
    if not correct_auth:
        return fastapi.HTTPException(status_code=fastapi.status.HTTP_401_UNAUTHORIZED)
    docker_client = docker.from_env()
    containers = docker_client.containers.list()
    for container in containers:
        logger.info(f" Container name: {container.name}, with id: {container.short_id}")
        if GATEWAY_IMAGE_NAME in container.image.tags[0]:
            logger.info(
                f"Restarting container {container.name}, with id: {container.short_id}"
            )
            container.restart()
            return (
                f"Restarted container {container.name}, with id: {container.short_id}"
            )
    return "gateway not found"


if __name__ == "__main__":
    uvicorn.run("poc:app", host="0.0.0.0", port=8001)
