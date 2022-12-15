import paho.mqtt.client as mqtt
from loguru import logger

###
#
#   mosquitto_sub -h 172.16.12.207 -p 31883 -u admin -P admin -t 'application/4/#' -v
###


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # client.subscribe("application/4/#")
    client.subscribe("application/7/#")


def on_message(client, userdata, message):
    logger.info(message.topic + ": " + message.payload.decode("utf-8"))


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set("admin", "admin")
client.connect("172.16.12.207", 31883, 60)

client.loop_forever()
