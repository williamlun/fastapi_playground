"""Converter class for graphDB"""
import os
from typing import Union
import json


import pandas as pd
import yaml
from loguru import logger

import excel_schema
import internal_schema

NETWORK_SERVER_NAME = "-network-server"
NETWORK_SERVER = "chirpstack-ns"

SERVICE_PROFILE_NAME = "-service-profile"
CHIRPSTACK = "chirpstack"


def fixed_resource(
    site_name: str,
) -> dict[internal_schema.ResourceType, list[internal_schema.ResourceBaseModel]]:
    resource: dict[
        internal_schema.ResourceType, list[internal_schema.ResourceBaseModel]
    ] = {}
    resource[internal_schema.ResourceType.NETWORK_SERVER] = [
        internal_schema.NetworkServer(
            name=site_name + NETWORK_SERVER_NAME,
            server=NETWORK_SERVER,
            port=8000,
        )
    ]

    resource[internal_schema.ResourceType.ORGANIZATION] = [
        internal_schema.Organization(name=CHIRPSTACK, displayName=CHIRPSTACK),
        internal_schema.Organization(name=site_name, displayName=site_name),
    ]

    resource[internal_schema.ResourceType.SERVICE_PROFILE] = [
        internal_schema.ServiceProfile(
            name=site_name + SERVICE_PROFILE_NAME,
            networkServer=site_name + NETWORK_SERVER_NAME,
            organization=site_name,
        ),
        internal_schema.ServiceProfile(
            name="test" + SERVICE_PROFILE_NAME,
            networkServer=site_name + NETWORK_SERVER_NAME,
            organization=CHIRPSTACK,
        ),
    ]
    return resource


def convert_gateway_profile(
    site_name: str, dataframe: pd.DataFrame
) -> dict[internal_schema.ResourceType, list[internal_schema.ResourceBaseModel]]:
    gateway_profile_resource: dict[
        internal_schema.ResourceType, list[internal_schema.ResourceBaseModel]
    ] = {}

    gateway_profile_resource[internal_schema.ResourceType.GATEWAY_PROFILE] = [
        internal_schema.GatewayProfile(
            name=gateway_profile,
            networkServer=site_name + NETWORK_SERVER_NAME,
        )
        for gateway_profile in list(set(dataframe["gatewayProfile"].tolist()))
    ]
    return gateway_profile_resource


def convert_gateway(
    site_name: str, dataframe: pd.DataFrame
) -> dict[internal_schema.ResourceType, list[internal_schema.ResourceBaseModel]]:
    gateway_resource: dict[
        internal_schema.ResourceType, list[internal_schema.ResourceBaseModel]
    ] = {}
    gateway_resource[internal_schema.ResourceType.GATEWAY] = [
        internal_schema.Gateway(
            name=gateway.gatewayProfile + "-" + gateway.id,
            id=gateway.id,
            organization=site_name,
            networkServer=site_name + NETWORK_SERVER_NAME,
            serviceProfile=site_name + SERVICE_PROFILE_NAME,
            gatewayProfile=gateway.gatewayProfile,
        )
        for gateway in [
            excel_schema.Gateaway(**row) for row in dataframe.to_dict(orient="records")
        ]
    ]
    return gateway_resource


def convert_device_profile(
    site_name: str, dataframe: pd.DataFrame
) -> dict[internal_schema.ResourceType, list[internal_schema.ResourceBaseModel]]:
    device_profile_resources = {}
    devices_profile_list: list[internal_schema.ResourceBaseModel] = []
    application_list: list[internal_schema.ResourceBaseModel] = []
    try:
        with open(
            "./templates/alarms_rule/device_profile_fields.yaml",
            "r",
            encoding="utf-8",
        ) as f:
            device_profile_fields_mapping: dict[str, list[str]] = yaml.load(
                f, Loader=yaml.FullLoader
            )
            logger.info("device_profile_fields_mapping read successfully.")
        with open(
            "./templates/alarms_rule/sensor_field_alarms_mapping.yaml",
            "r",
            encoding="utf-8",
        ) as f:
            sensor_field_alarms_mapping: dict[str, list[str]] = yaml.load(
                f, Loader=yaml.FullLoader
            )
            logger.info("sensor_field_alarms_mapping read successfully.")
    except IOError as e:
        logger.error("Template Read Failed.")
        raise e from e

    for device_profile in [
        excel_schema.DeviceProfile(**row) for row in dataframe.to_dict(orient="records")
    ]:

        chirpstack_profile = device_profile.dict().copy()
        chirpstack_profile[
            "payloadDecoderScript"
        ] = f"codex/{device_profile.name}/decode.js"
        chirpstack_profile[
            "payloadEncoderScript"
        ] = f"codex/{device_profile.name}/encode.js"
        chirpstack_profile["networkServer"] = site_name + NETWORK_SERVER_NAME
        chirpstack_profile["organization"] = site_name
        chirpstack_profile["uplinkInterval"] = (
            chirpstack_profile["uplinkInterval"] + "s"
        )

        thingsboard_profile: dict[str, Union[str, list[internal_schema.Alarm]]] = {}
        thingsboard_profile["rule_chain"] = device_profile.ruleEngine

        if device_profile.name not in device_profile_fields_mapping:
            logger.error("device profile not found in device profile fields list")

        sensor_fields = device_profile_fields_mapping.get(device_profile.name, [])

        alarm_names = []
        for sensor_field in sensor_fields:
            alarm_names.extend(
                [
                    alarm + "_" + sensor_field.upper()
                    for alarm in sensor_field_alarms_mapping.get(sensor_field, [])
                ]
            )

        alarms = [internal_schema.Alarm(type=alarm_name) for alarm_name in alarm_names]

        thingsboard_profile["alarms"] = alarms

        devices_profile_list.append(
            internal_schema.DeviceProfile(
                name=device_profile.name,
                chirpstack=chirpstack_profile,
                thingsboard=thingsboard_profile,
            )
        )

        application_list.append(
            internal_schema.Application(
                name=device_profile.name,
                serviceProfile=site_name + SERVICE_PROFILE_NAME,
                organization=site_name,
                description="application of " + device_profile.name,
            )
        )

    device_profile_resources[
        internal_schema.ResourceType.DEVICE_PROFILE
    ] = devices_profile_list
    device_profile_resources[
        internal_schema.ResourceType.APPLICATION
    ] = application_list
    return device_profile_resources


def convert_device(
    dataframe: pd.DataFrame,
    excel_resources: dict[excel_schema.ResourceType, pd.DataFrame],
) -> dict[internal_schema.ResourceType, list[internal_schema.ResourceBaseModel]]:
    device_resources: dict[
        internal_schema.ResourceType, list[internal_schema.ResourceBaseModel]
    ] = {}
    device_list: list[internal_schema.ResourceBaseModel] = []
    for device in [
        excel_schema.Device(**row) for row in dataframe.to_dict(orient="records")
    ]:

        my_alarm_attribute = {}
        df_def_alarm_setting = excel_resources[
            excel_schema.ResourceType.DEFAULT_ALARMS_SETTING
        ]
        df_match_data_def_setting = df_def_alarm_setting.loc[
            df_def_alarm_setting["deviceProfile"] == device.deviceProfile
        ]
        for row in df_match_data_def_setting.to_dict(orient="records"):
            key = (
                row["conditionType"]
                + "_"
                + row["operator"]
                + "_"
                + row["field"]
                + "_"
                + row["attribute"]
            )
            my_alarm_attribute.update({key: row["value"]})

        df_alarm_setting = excel_resources[excel_schema.ResourceType.ALARMS_SETTING]
        df_match_data_setting = df_alarm_setting.loc[
            df_alarm_setting["deviceName"] == device.id
        ]

        for row in df_match_data_setting.to_dict(orient="records"):
            key = (
                row["conditionType"]
                + "_"
                + row["operator"]
                + "_"
                + row["field"]
                + "_"
                + row["attribute"]
            )
            my_alarm_attribute.update({key: row["value"]})

        my_rule_chain_attribute = {}
        df_rule = excel_resources[excel_schema.ResourceType.SENSOR_READING_TO_BACNET]
        df_match_data_rule = df_rule.loc[df_rule["fromDevice"] == device.id]
        for row in df_match_data_rule.to_dict(orient="records"):
            value = row["objectType"] + "-" + str(row["object"])
            my_rule_chain_attribute.update({row["field"]: value})

        my_relations_list = [
            internal_schema.Device.InThingsboard.Relation(
                from_device=(
                    device.deviceProfile + "-" + device.id
                    if device.deviceProfile != "default"
                    else device.id
                ),
                to_device=row["toDevice"],
                type=internal_schema.RelationType.CONTAINS,
            )
            for row in df_match_data_rule.to_dict(orient="records")
        ]

        my_thingsboard = internal_schema.Device.InThingsboard(
            alarms_attribute=my_alarm_attribute,
            rule_chain_attribute=my_rule_chain_attribute,
            relations=my_relations_list,
        )

        my_device_variables = {}
        generic_device = {}
        df_match_generic_device = excel_resources[
            excel_schema.ResourceType.GENERIC_DEVICE
        ].loc[
            excel_resources[excel_schema.ResourceType.GENERIC_DEVICE]["id"] == device.id
        ]
        if not df_match_generic_device.empty:
            for row in df_match_generic_device.to_dict(orient="records"):
                generic_device.update({row["object"]: str(row["fieldName"])})
            my_device_variables.update({"generic_device": json.dumps(generic_device)})

        sensor_calibration = {}
        df_match_sensor_calibration = excel_resources[
            excel_schema.ResourceType.SENSOR_CALIBRATION
        ].loc[
            excel_resources[excel_schema.ResourceType.SENSOR_CALIBRATION]["id"]
            == device.id
        ]

        for row in df_match_sensor_calibration.to_dict(orient="records"):
            sensor_calibration.update({row["fieldName"] + "Scale": row["scale"]})
            sensor_calibration.update({row["fieldName"] + "Offset": row["offset"]})
        my_device_variables.update(
            {"sensor_calibration": json.dumps(sensor_calibration)}
        )

        my_chirpstack_device = device.dict().copy()
        my_chirpstack_device["devEUI"] = my_chirpstack_device.pop("id")
        my_chirpstack_device["application"] = device.deviceProfile
        my_chirpstack_device["description"] = device.description
        my_chirpstack_device["variables"] = my_device_variables

        my_chirpstack = internal_schema.Device.InChirpstack(**my_chirpstack_device)

        if device.deviceProfile == "default":
            device_list.insert(
                0,
                internal_schema.Device(
                    name=device.id,
                    deviceProfile=device.deviceProfile,
                    thingsboard=my_thingsboard,
                    chirpstack=my_chirpstack,
                ),
            )
        else:
            device_list.append(
                internal_schema.Device(
                    name=device.deviceProfile + "-" + device.id,
                    deviceProfile=device.deviceProfile,
                    thingsboard=my_thingsboard,
                    chirpstack=my_chirpstack,
                )
            )

    device_resources[internal_schema.ResourceType.DEVICE] = device_list
    return device_resources


def get_rule_chain(
    config: excel_schema.Config,
) -> list[internal_schema.ResourceBaseModel]:
    rule_list: list[internal_schema.ResourceBaseModel] = []
    rule_names = [
        filename.split(".")[0]
        for filename in os.listdir(os.getcwd() + "/templates/rule_chains")
    ]
    for rule_name in rule_names:
        rule_chain = internal_schema.RuleChain(name=rule_name)
        if rule_chain.name is internal_schema.RuleChain.Name.SEND_EVENTS_TO_KAFKA.value:
            rule_chain.additional_config = internal_schema.RuleChain.KafkaConfig(
                kafka_cluster_url=config.thingsboard.kafka.url,
                kafka_security_protocol=config.thingsboard.kafka.security_protocol,
                kafka_sasl_mechanism=config.thingsboard.kafka.sasl_mechanism,
                kafka_username=config.thingsboard.kafka.username,
                kafka_password=config.thingsboard.kafka.password,
            )
        rule_list.append(rule_chain)
    return rule_list


def add_gateway_as_thingsboard_device(
    site_name: str,
    devices: list[internal_schema.ResourceBaseModel],
) -> list[internal_schema.ResourceBaseModel]:

    additional_info = {
        "gateway": True,
        "description": "",
        "overwriteActivityTime": False,
    }
    gateway_device = internal_schema.Device(
        name=site_name + "-gateway",
        deviceProfile="default",
        thingsboard=internal_schema.Device.InThingsboard(
            additionalInfo=additional_info
        ),
        chirpstack=internal_schema.Device.InChirpstack(),
    )
    devices.append(gateway_device)
    return devices


def create_internal_resources(
    site_name: str,
    resources: dict[excel_schema.ResourceType, pd.DataFrame],
    config: excel_schema.Config,
) -> tuple[
    dict[internal_schema.ResourceType, list[internal_schema.ResourceBaseModel]],
    dict[internal_schema.ResourceType, list[internal_schema.ResourceBaseModel]],
]:
    chirpstack_resource = fixed_resource(site_name)
    chirpstack_resource.update(
        convert_gateway_profile(site_name, resources[excel_schema.ResourceType.GATEWAY])
    )
    chirpstack_resource.update(
        convert_device_profile(
            site_name, resources[excel_schema.ResourceType.DEVICE_PROFILE]
        )
    )
    chirpstack_resource.update(
        convert_gateway(site_name, resources[excel_schema.ResourceType.GATEWAY])
    )
    chirpstack_resource.update(
        convert_device(resources[excel_schema.ResourceType.DEVICE], resources)
    )

    thingsboard_resource = {}
    thingsboard_resource[internal_schema.ResourceType.RULE_CHAIN] = get_rule_chain(
        config
    )
    thingsboard_resource[
        internal_schema.ResourceType.DEVICE_PROFILE
    ] = chirpstack_resource[internal_schema.ResourceType.DEVICE_PROFILE]
    thingsboard_resource[
        internal_schema.ResourceType.DEVICE
    ] = add_gateway_as_thingsboard_device(
        site_name, chirpstack_resource[internal_schema.ResourceType.DEVICE]
    )

    return chirpstack_resource, thingsboard_resource
