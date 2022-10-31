"""From Excel data to internal schema object"""
from typing import Optional

import pandas as pd
import yaml
from loguru import logger

import config_schema
import excel_schema
import exception


def get_type(sensor_field_name: str) -> str:
    if (
        sensor_field_name.startswith("is")
        or sensor_field_name.startswith("has")
        or sensor_field_name.startswith("relay")
    ):
        return "boolean"
    return "double"


def get_value(sensor_field_name: str) -> str:
    if sensor_field_name in ("rssi", "loRaSNR"):
        return "${rxInfo[0]." + sensor_field_name + "}"
    return "${object." + sensor_field_name + "}"


def generate_mqtt_config(
    site_name: str,
    applications: list[dict],
    config: excel_schema.Config,
) -> config_schema.MqttConfig:
    security_dict = config_schema.MqttConfig.Broker.Security(
        username=config.chirpstack.mqtt_username,
        password=config.chirpstack.mqtt_password,
    )

    broker_dict = config_schema.MqttConfig.Broker(
        name=site_name,
        host=config.chirpstack.host,
        port=config.chirpstack.mqtt_port,
        clientId=site_name + "-MQTT-CLIENT",
        security=security_dict,
    )

    try:
        with open(
            "./templates/alarms_rule/device_profile_fields.yaml",
            "r",
            encoding="utf-8",
        ) as f:
            device_alarm_list: dict = yaml.load(f, Loader=yaml.FullLoader)
            logger.info("device_alarm_list read successfully.")
    except IOError as exc:
        logger.error("device_alarm_list Read Failed.")
        raise exception.ResourceNotFoundError(
            "./templates/alarms_rule/device_profile_fields.yaml not found"
        ) from exc

    mappings = []
    for application in applications:
        id_ = application["id"]
        name = application["name"]
        sensor_fields = device_alarm_list.get(name, [])

        time_series_fields = [
            config_schema.MqttConfig.MappingUnit.Converter.ValueMapper(
                type=get_type(sensor_field),
                key=sensor_field,
                value=get_value(sensor_field),
            )
            for sensor_field in sensor_fields
        ]

        attributes = [
            config_schema.MqttConfig.MappingUnit.Converter.ValueMapper(
                type="int",
                key="applicationID",
                value="${applicationID}",
            ),
            config_schema.MqttConfig.MappingUnit.Converter.ValueMapper(
                type="string",
                key="deviceID",
                value="${devEUI}",
            ),
        ]

        converter = config_schema.MqttConfig.MappingUnit.Converter(
            deviceNameJsonExpression="${deviceName}",
            deviceTypeTopicExpression="${applicationName}",
            attributes=attributes,
            timeseries=time_series_fields,
        )

        mapping_unit = config_schema.MqttConfig.MappingUnit(
            topicFilter="application/" + id_ + "/device/+/event/up",
            converter=converter,
        )

        mappings.append(mapping_unit)

    result = config_schema.MqttConfig(
        broker=broker_dict,
        mapping=mappings,
    )
    return result


def generate_backnet_config(
    site_name: str, resources: dict[excel_schema.ResourceType, pd.DataFrame]
) -> Optional[config_schema.BACnetConfig]:
    backnet_df = resources[excel_schema.ResourceType.SENSOR_READING_TO_BACNET]
    backnet_devices = list(set(backnet_df["toDevice"]))
    if len(backnet_devices) > 1:
        raise exception.MultiableBacknetGatewayError("More then one backnet_devices")
    elif len(backnet_devices) == 0:
        logger.info("No bacnet devices found in SENSOR_READING_TO_BACNET")
        return None
    else:
        backnet_device = backnet_devices[0]

    splitname = backnet_device.split("-")
    ip = ".".join(splitname[2:6])
    port = splitname[6]

    server_side_rpcs = []
    methods = backnet_df["objectType"] + ":" + backnet_df["object"].astype(str)

    server_side_rpcs = [
        config_schema.BACnetConfig.Device.ServerSideRpcUnit(
            method="setValue" + method.replace(":", "-"),
            objectId=method[0].lower() + method[1:],
        )
        for method in methods.to_list()
    ]

    attributes = [
        config_schema.BACnetConfig.Device.ValueMapper(
            key="testAttribute",
            type="double",
            objectId="analogValue:1",
        )
    ]
    timeseries = [
        config_schema.BACnetConfig.Device.ValueMapper(
            key="testTimeseries",
            type="double",
            objectId="binaryValue:1",
        )
    ]

    device_dict = config_schema.BACnetConfig.Device(
        deviceName=backnet_device,
        address=ip + ":" + port,
        attributes=attributes,
        timeseries=timeseries,
        serverSideRpc=server_side_rpcs,
    )

    general_dict = config_schema.BACnetConfig.General(
        objectName=site_name + " BACnet gateway",
        address="0.0.0.0:" + port,
        objectIdentifier=599,
    )

    result = config_schema.BACnetConfig(
        general=general_dict,
        devices=[device_dict],
    )

    return result


def generate_gateaway_config(
    access_token: str,
    config: excel_schema.Config,
    has_bacnet_device: bool,
) -> config_schema.GatewayGeneralConfig:

    security = config_schema.GatewayGeneralConfig.ThingsBoard.Security(
        accessToken=access_token
    )
    thingsboard = config_schema.GatewayGeneralConfig.ThingsBoard(
        host=config.thingsboard.host,
        port=int(config.thingsboard.mqtt_port),
        security=security,
    )

    mqtt_connector = config_schema.GatewayGeneralConfig.Connector(
        name="MQTT Broker Connector",
        type="mqtt",
        configuration="mqtt.json",
    )
    connectors = [mqtt_connector]

    if has_bacnet_device:
        bacnet_connector = config_schema.GatewayGeneralConfig.Connector(
            name="BACnet Connector",
            type="bacnet",
            configuration="bacnet.json",
        )
        connectors.append(bacnet_connector)

    return config_schema.GatewayGeneralConfig(
        thingsboard=thingsboard,
        connectors=connectors,
    )
