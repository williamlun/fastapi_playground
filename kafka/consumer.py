import confluent_kafka
from loguru import logger

consumer = confluent_kafka.Consumer(
    {"bootstrap.servers": "localhost:9092", "group.id": "hi"}
)
consumer.subscribe([".*"])


while True:
    msg = consumer.poll(timeout=1.0)
    if msg is None:
        continue

    logger.info(f"Received from [{msg.topic()}]: {msg.value()}")
