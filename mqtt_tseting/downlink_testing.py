import paho.mqtt.client as mqtt
import json

# Define the broker and topic
broker_address = "172.16.14.50"

Application_id = "1"
device_ids = [
    "7012018a99999999",
    "7012018a99999998",
    "7012018a99999997",
]

topic = "application/64/device/[DevEUI]/command/down"

data = {
    "confirmed": True,
    "fPort": 999,
    "object": {"temperatureSensor": {"1": 25}, "humiditySensor": {"1": 32}},
}
# Create a client instance
client = mqtt.Client()

# Connect to the broker
client.username_pw_set("ataladmin", "381rm1hOvGFfe8")
client.connect(broker_address, 31883, 60)

# Publish a message
for device_id in device_ids:
    topic = topic.replace("[DevEUI]", device_id)
    client.publish(topic, json.dumps(data))

# Disconnect from the broker
client.disconnect()
