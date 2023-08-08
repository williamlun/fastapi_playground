import paho.mqtt.client as mqtt
import json

# Define the broker and topic
broker_address = "localhost"
# topic = "application/81/device/7012018a99999999/event/up"
topic = "#"

# with open(
#     "/Users/williamleung/Documents/fastapi_playground/text_edit/asdfs.json", "r"
# ) as f:
#     json_data = f.read()
# json_obj = json.loads(json_data)
json_obj = {"value": "stuff"}
# Create a client instance
client = mqtt.Client()

# Connect to the broker
client.username_pw_set("admin", "admin")
client.connect(broker_address, 1883, 60)

# Publish a message

client.publish(topic, json.dumps(json_obj))

# Disconnect from the broker
client.disconnect()
