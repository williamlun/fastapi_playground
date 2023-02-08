import confluent_kafka
from loguru import logger


TOPIC = "realtime-weather-data"
GROUP_ID = "monitor"


def init_kafka():
    consumer = confluent_kafka.Consumer(
        {
            "bootstrap.servers": "localhost:9092",
            "group.id": GROUP_ID,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": "false",
            "security.protocol": "PLAINTEXT",
            "sasl.mechanisms": "PLAIN",
            "sasl.username": "",
            "sasl.password": "",
        }
    )
    consumer.subscribe([TOPIC])
    return consumer


def main():
    consumer = init_kafka()
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        logger.info(f"Received message: {msg.value()}")


if __name__ == "__main__":
    main()
