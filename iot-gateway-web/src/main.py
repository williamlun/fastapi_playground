"""small fastapi for import iot gateway config file"""

import fastapi
import uvicorn
import os
import shutil
from loguru import logger

app = fastapi.FastAPI()

MQTT_PATH = os.getenv("MQTT_PATH", "a.txt")
BACKNET_PATH = os.getenv("BACKNET_PATH", "/config/bacnet.json")
TB_GATEWAY_PATH = os.getenv("TB_GATEWAY_PATH", "/config/tb_gateway.yaml")


@app.get("/probes/healthiness")
def healthiness():
    return


@app.post("/mqtt-config")
async def read_config(file: fastapi.UploadFile):
    try:
        content = file.file.read()
        fdst = open(MQTT_PATH, "w")
        shutil.copyfileobj(content, fdst)
        logger.info(f"mqtt config saved to {MQTT_PATH}")
        return f"mqtt config saved to {MQTT_PATH}"
    except BaseException as e:  # pylint: disable=broad-except
        logger.exception(e)
        raise fastapi.exceptions.HTTPException(status_code=500, detail=e)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001)
