"""Import data function"""
from typing import Dict, Type


import pandas as pd
from loguru import logger
import json
import yaml

import services.config_converter
import services.graphdb_converter
import services.platform_converter
import stores.chirpstack.base
import stores.thingsboard.base

import stores.chirpstack.network_server
import stores.chirpstack.gateway_profile
import stores.chirpstack.organization
import stores.chirpstack.service_profile
import stores.chirpstack.device_profile
import stores.chirpstack.gateway
import stores.chirpstack.application
import stores.chirpstack.device

import stores.thingsboard.rule_chain
import stores.thingsboard.device_profile
import stores.thingsboard.device

import stores.neo4j.gdb_client
import stores.neo4j.base
import stores.neo4j.site
import stores.neo4j.device
import stores.neo4j.field


import graphdb_schema
import excel_schema
import internal_schema
import exception

CHRIPSTACK_RESOURCE_IMPORT_ORDER = [
    internal_schema.ResourceType.NETWORK_SERVER,
    internal_schema.ResourceType.GATEWAY_PROFILE,
    internal_schema.ResourceType.ORGANIZATION,
    internal_schema.ResourceType.SERVICE_PROFILE,
    internal_schema.ResourceType.GATEWAY,
    internal_schema.ResourceType.DEVICE_PROFILE,
    internal_schema.ResourceType.APPLICATION,
    internal_schema.ResourceType.DEVICE,
]
THINGSBOARD_RESOURCE_IMPORT_ORDER = [
    internal_schema.ResourceType.RULE_CHAIN,
    internal_schema.ResourceType.DEVICE_PROFILE,
    internal_schema.ResourceType.DEVICE,
]

GRAPHDB_RESOURCE_IMPORT_ORDER = [
    graphdb_schema.ResourceType.SITE,
    graphdb_schema.ResourceType.FIELD,
    graphdb_schema.ResourceType.DEVICE,
]


def import_resource(
    site_name: str,
    df_resources: Dict[excel_schema.ResourceType, pd.DataFrame],
    config: excel_schema.Config,
):

    (
        chirpstack_resource,
        thingsboard_resource,
    ) = services.platform_converter.create_internal_resources(
        site_name, df_resources, config
    )

    for resource_type in CHRIPSTACK_RESOURCE_IMPORT_ORDER:
        logger.info(f"Creating chirpstack resource of ----{resource_type.value}------")
        resource = chirpstack_resource[resource_type]
        resource_store_for_chirpstack = _get_chirpstack_store(resource_type)
        for data in resource:
            try:
                resource_store_for_chirpstack.create(data)
            except exception.ResourceAlreadyExistsError:
                resource_store_for_chirpstack.update(data)
            except BaseException as exc:
                logger.exception(f"{exc}")
                raise exc

    # custom root rule chain handling
    rule_chain_client = stores.thingsboard.rule_chain.RuleChain()
    for rule_chain in thingsboard_resource[internal_schema.ResourceType.RULE_CHAIN]:
        if rule_chain.name == "SEND_EVENTS_TO_KAFKA":
            rule_chain_ = internal_schema.RuleChain(**rule_chain.dict())
            try:
                rule_chain_client.create(rule_chain_)
            except exception.ResourceAlreadyExistsError:
                rule_chain_client.update(rule_chain_)
            except BaseException as exc:
                logger.exception(f"{exc}")
                raise exc

    root_rule_chain = rule_chain_client.get_id_by_name("SEND_EVENTS_TO_KAFKA")
    rule_chain_client.set_default_rule_chain(root_rule_chain.id)

    for resource_type in THINGSBOARD_RESOURCE_IMPORT_ORDER:
        logger.info(f"Creating thingsboard resource of ----{resource_type.value}------")
        resource = thingsboard_resource[resource_type]
        resource_store_for_thingsboard = _get_thingsboard_store(resource_type)
        for data in resource:
            try:
                resource_store_for_thingsboard.create(data)
            except exception.ResourceAlreadyExistsError:
                resource_store_for_thingsboard.update(data)
            except exception.DecodingScriptNotFoundError:
                pass
            except BaseException as exc:
                logger.exception(f"{exc}")
                raise exc

    bacnet_config = services.config_converter.generate_backnet_config(
        site_name, df_resources
    )
    if bacnet_config is not None:
        _export_json_file(bacnet_config.dict(), config.export_path + "bacnet.json")

    application_client = stores.chirpstack.application.Application()
    applications = application_client.raw_read()
    mqtt_config = services.config_converter.generate_mqtt_config(
        site_name, applications, config
    )
    _export_json_file(mqtt_config.dict(), config.export_path + "mqtt.json")

    thingsboard_device_client = stores.thingsboard.device.Device()
    general_id = thingsboard_device_client.get_id_by_name(site_name + "-gateway")
    access_token = thingsboard_device_client.read_credentials_by_id(general_id.id)
    gateway_config = services.config_converter.generate_gateaway_config(
        access_token, config, bacnet_config is not None
    )
    with open(config.export_path + "tb_gateway.yaml", "w", encoding="utf-8") as f:
        yaml.dump(gateway_config.dict(), f)
        logger.info(f"export yaml file: {config.export_path}tb_gateway.yaml")


def _export_json_file(data: dict, path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)
        logger.info(f"export json file: {path}")


def _get_chirpstack_store(
    resource_type: internal_schema.ResourceType,
) -> stores.chirpstack.base.Resource:
    resource_mapping: Dict[
        internal_schema.ResourceType, Type[stores.chirpstack.base.Resource]
    ] = {
        internal_schema.ResourceType.NETWORK_SERVER: stores.chirpstack.network_server.NetworkServer,
        internal_schema.ResourceType.GATEWAY_PROFILE: stores.chirpstack.gateway_profile.GatewayProfile,
        internal_schema.ResourceType.ORGANIZATION: stores.chirpstack.organization.Organization,
        internal_schema.ResourceType.SERVICE_PROFILE: stores.chirpstack.service_profile.ServiceProfile,
        # need fix
        internal_schema.ResourceType.GATEWAY: stores.chirpstack.gateway.Gateway,
        internal_schema.ResourceType.DEVICE_PROFILE: stores.chirpstack.device_profile.DeviceProfile,
        internal_schema.ResourceType.APPLICATION: stores.chirpstack.application.Application,
        internal_schema.ResourceType.DEVICE: stores.chirpstack.device.Device,
    }
    return resource_mapping[resource_type]()


def _get_thingsboard_store(
    resource_type: internal_schema.ResourceType,
) -> stores.thingsboard.base.Resource:
    resource_mapping: Dict[
        internal_schema.ResourceType, Type[stores.thingsboard.base.Resource]
    ] = {
        internal_schema.ResourceType.DEVICE_PROFILE: stores.thingsboard.device_profile.DeviceProfile,
        internal_schema.ResourceType.DEVICE: stores.thingsboard.device.Device,
        internal_schema.ResourceType.RULE_CHAIN: stores.thingsboard.rule_chain.RuleChain,
    }
    return resource_mapping[resource_type]()


def _get_graphdb_store(
    resource_type: graphdb_schema.ResourceType,
) -> stores.neo4j.base.Resource:
    resource_mapping: dict[
        graphdb_schema.ResourceType, Type[stores.neo4j.base.Resource]
    ] = {
        graphdb_schema.ResourceType.SITE: stores.neo4j.site.Site,
        graphdb_schema.ResourceType.FIELD: stores.neo4j.field.Field,
        graphdb_schema.ResourceType.DEVICE: stores.neo4j.device.Device,
    }
    return resource_mapping[resource_type]()


def import_to_graphdb(
    site_name: str,
    df_resources: Dict[excel_schema.ResourceType, pd.DataFrame],
):
    (
        site_node,
        fields_node,
        devices_node,
    ) = services.graphdb_converter.create_gdb_resource(site_name, df_resources)

    logger.info("Creating GraphDB resource of ---- SITES ------")
    stores.neo4j.site.Site().merge_create(site_node)

    logger.info("Creating GraphDB resource of -----FIELDS-----")
    for field in fields_node:
        stores.neo4j.field.Field().merge_create(field)

    logger.info("Creating GraphDB resource of -----DEVICES-----")
    for device in devices_node:
        stores.neo4j.device.Device().merge_create(device)
