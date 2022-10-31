"""From Excel data to internal schema object"""
import uuid

import pandas as pd
import yaml
from loguru import logger

import excel_schema
import graphdb_schema


def read_device_field_mapping() -> dict[str, list[str]]:
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
    except IOError as e:
        logger.error("Template Read Failed.")
        raise e from e

    return device_profile_fields_mapping


def create_gdb_resource(
    site_name: str,
    resources: dict[excel_schema.ResourceType, pd.DataFrame],
) -> tuple[
    graphdb_schema.Site, list[graphdb_schema.Field], list[graphdb_schema.Device]
]:

    site = graphdb_schema.Site(
        name=site_name,
        displayName=site_name.lower(),
        id=uuid.uuid5(uuid.NAMESPACE_OID, site_name),
    )

    device_profile_fields_mapping = read_device_field_mapping()

    device_profiles_df = resources[excel_schema.ResourceType.DEVICE]
    device_profiles = list(set(device_profiles_df["deviceProfile"]))
    fields_name = []
    for device_profile in device_profiles:
        fields_name.extend(device_profile_fields_mapping.get(device_profile, []))
    fields = [graphdb_schema.Field(name=field) for field in list(set(fields_name))]

    device_profile_fields_mapping = read_device_field_mapping()
    device_df = resources[excel_schema.ResourceType.DEVICE]
    devices = []
    for device in [
        excel_schema.Device(**row) for row in device_df.to_dict(orient="records")
    ]:
        device_name = device.deviceProfile + "-" + device.id
        relation = [
            graphdb_schema.Relation(
                node_type=graphdb_schema.ResourceType.HAS_LOCATION, to_node=site
            )
        ]

        for field in device_profile_fields_mapping.get(device.deviceProfile, []):
            relation.append(
                graphdb_schema.Relation(
                    node_type=graphdb_schema.ResourceType.HAS_POINT,
                    to_node=graphdb_schema.Field(name=field),
                )
            )
        device_node = graphdb_schema.Device(
            id=uuid.uuid5(uuid.NAMESPACE_OID, device_name),
            name=device_name,
            displayName=device.description,
            relations=relation,
        )
        devices.append(device_node)

    return site, fields, devices
