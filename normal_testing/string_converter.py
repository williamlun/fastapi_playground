list_of_d = [
    {"name": "env.CHIRPSTACK_HOST", "value": "${chirpstack_host}"},
    {"name": "env.CHIRPSTACK_PORT", "value": "${chirpstack_port}"},
    {"name": "env.CHIRPSTACK_USERNAME", "value": "${chirpstack_username}"},
    {"name": "env.CHIRPSTACK_PASSWORD", "value": "${chirpstack_password}"},
    {"name": "env.CHIRPSTACK_MQTT_HOST", "value": "${chirpstack_mqtt_host}"},
    {"name": "env.CHIRPSTACK_MQTT_PORT", "value": "${chirpstack_mqtt_port}"},
    {"name": "env.CHIRPSTACK_MQTT_USERNAME", "value": "${chirpstack_mqtt_username}"},
    {"name": "env.CHIRPSTACK_MQTT_PASSWORD", "value": "${chirpstack_mqtt_password}"},
    {"name": "env.THINGSBOARD_HOST", "value": "${thingsboard_host}"},
    {"name": "env.THINGSBOARD_PORT", "value": "${thingsboard_port}"},
    {"name": "env.THINGSBOARD_USERNAME", "value": "${thingsboard_username}"},
    {"name": "env.THINGSBOARD_PASSWORD", "value": "${thingsboard_password}"},
    {"name": "env.DEVICE_STATUS_TOLERANCE", "value": "${device_status_tolerance}"},
    {
        "name": "env.DEVICE_STATUS_REFRESH_INTERVAL",
        "value": "${device_status_refresh_interval}",
    },
    {"name": "imagePullSecrets[0].name", "value": "${image_pull_secret_name}"},
]

for d in list_of_d:
    print("parameter {")
    print(f'    name = "{d["name"]}"')
    value = d["value"].replace("$", "var.").replace("{", "").replace("}", "")
    print(f"    value = {value}")
    print("}")
