import asyncio_mqtt as aiomqtt
import asyncio
from loguru import logger

CHIRPSTACK_MQTT_HOST = "172.16.14.50"
CHIRPSTACK_MQTT_PORT = 31883
CHIRPSTACK_MQTT_USERNAME = "ataladmin"
CHIRPSTACK_MQTT_PASSWORD = "381rm1hOvGFfe8"


async def gateway_client():
    async with aiomqtt.Client(
        hostname=CHIRPSTACK_MQTT_HOST,
        port=CHIRPSTACK_MQTT_PORT,
        username=CHIRPSTACK_MQTT_USERNAME,
        password=CHIRPSTACK_MQTT_PASSWORD,
    ) as client:
        async with client.messages() as messages:
            await client.subscribe([("gateway/+/state/conn", 0)])
            logger.info("Subscribed to MQTT broker with topic gateway/+/state/conn")
            async for message in messages:
                print(message.topic.value.split("/")[1])


async def geteway_client_loop_handler():
    while True:
        try:
            async with asyncio.timeout(60 * 60):
                await gateway_client()
        except asyncio.TimeoutError:
            pass


asyncio.run(geteway_client_loop_handler())
