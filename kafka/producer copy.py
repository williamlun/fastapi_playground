import confluent_kafka
import random
from loguru import logger
import time
import json
import datetime
import uuid
import requests
import pydantic

TOPIC = "ATALDEV-bms-service-point-value"


def get_data() -> dict:
    data = {
        "id": str(uuid.uuid4()),
        "timestamp": str(datetime.datetime.now()),
        "value": True,
    }
    return data


def init_kafka():
    return confluent_kafka.Producer(
        {
            "bootstrap.servers": "172.16.14.49:30094",
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
        data = get_data()
        kafka_pro_client.produce(TOPIC, json.dumps(data).encode("utf-8"), callback=ack)
        kafka_pro_client.poll(1)
        time.sleep(60)


if __name__ == "__main__":
    main()
