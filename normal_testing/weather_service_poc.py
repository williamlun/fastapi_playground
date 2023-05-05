import confluent_kafka

from loguru import logger
import time
import json
import requests
import pydantic

TOPIC = "realtime-weather-data"


class WeatherDataModel(pydantic.BaseModel):
    pass


def get_weather_data() -> dict:
    url = "https://api.openweathermap.org/data/2.5/weather?lat=51.5073219&lon=-0.1276474&appid=3b2ebdc259c724bb93180d5b3ad683bf"
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    result = response.json()
    logger.info(result)
    return result


def init_kafka():
    return confluent_kafka.Producer(
        {
            "bootstrap.servers": "localhost:9092",
            "security.protocol": "PLAINTEXT",
            "sasl.mechanisms": "PLAIN",
            "sasl.username": "",
            "sasl.password": "",
        }
    )


def ack(err, msg):
    if err is not None:
        logger.error(err)
    else:
        logger.info(
            f"Message sent to topic: {msg.topic()}, partition: {msg.partition()} with value: {msg.value()}"
        )


def main():

    kafka_pro_client = init_kafka()
    while True:
        data = get_weather_data()
        kafka_pro_client.produce(TOPIC, json.dumps(data).encode("utf-8"), callback=ack)
        kafka_pro_client.poll(1)
        time.sleep(60)


if __name__ == "__main__":
    main()
