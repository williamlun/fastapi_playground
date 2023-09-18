import confluent_kafka

from loguru import logger
import time
import json
import requests
import datetime
import pydantic
import random

TOPIC = "ATALDEV-bms-service-bms-data"


def init_kafka():
    return confluent_kafka.Producer(
        {
            "bootstrap.servers": "localhost:9094",
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
        my_data = {
            "id": "214570ce-c175-5bdd-9e2b-035203909444",
            "path": "/ChPlt/cooling_load",
            "timestamp": datetime.datetime.now().isoformat(),
            "value": round(random.uniform(1000, 2000), 1),
            "site_id": "78e71a60-326f-575b-9972-fb8b4f2df2f5",
            "site_name": "ATALDEV",
        }

        my_data2 = {
            "id": "6ab76e7a-f0f8-56db-bf46-e9753a44db88",
            "path": "/ChPlt/outdoor_wbtemp",
            "timestamp": datetime.datetime.now().isoformat(),
            "value": round(random.uniform(10, 30), 1),
            "site_id": "78e71a60-326f-575b-9972-fb8b4f2df2f5",
            "site_name": "ATALDEV",
        }

        my_data3 = {
            "id": "3f3a75b5-aede-54aa-8a06-1671f4a2bf9f",
            "path": "/ChPlt/cdws_temp",
            "timestamp": datetime.datetime.now().isoformat(),
            "value": round(random.uniform(10, 30), 1),
            "site_id": "78e71a60-326f-575b-9972-fb8b4f2df2f5",
            "site_name": "ATALDEV",
        }

        data1 = my_data
        kafka_pro_client.produce(TOPIC, json.dumps(data1).encode("utf-8"), callback=ack)
        kafka_pro_client.poll(1)
        data2 = my_data2
        kafka_pro_client.produce(TOPIC, json.dumps(data2).encode("utf-8"), callback=ack)
        kafka_pro_client.poll(1)
        data3 = my_data3
        kafka_pro_client.produce(TOPIC, json.dumps(data3).encode("utf-8"), callback=ack)
        kafka_pro_client.poll(1)
        time.sleep(10)


if __name__ == "__main__":
    main()
