import confluent_kafka
from confluent_kafka import Consumer
from loguru import logger

TOPIC = "^*"
GROUP_ID = "monitor"


def init_kafka():
    consumer = confluent_kafka.Consumer(
        {
            "bootstrap.servers": "172.16.14.49:30094",
            "group.id": GROUP_ID,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": "true",
            "security.protocol": "PLAINTEXT",
            "sasl.mechanisms": "PLAIN",
            "sasl.username": "",
            "sasl.password": "",
        }
    )
    consumer.subscribe(["^.*-bms-service-point-value"])
    return consumer


def main():
    consumer = init_kafka()
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        logger.info(f"Received message topic: {msg.topic()}")
        logger.info(f"Received message: {msg.value()}")


if __name__ == "__main__":
    main()
