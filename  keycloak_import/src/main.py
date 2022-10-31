"""Data entrance for thingbaord and chirpstack"""

from typing import Dict

import pandas as pd
import argparse
import yaml
from loguru import logger

import excel_schema

import services
import services.imports

import stores.chirpstack
import stores.thingsboard
import stores.chirpstack.conn_config
import stores.thingsboard.conn_config
import stores.neo4j.gdb_client


# import services.exports

RESOURCE_IN_EXCEL = [
    excel_schema.ResourceType.GATEWAY,
    excel_schema.ResourceType.DEVICE_PROFILE,
    excel_schema.ResourceType.DEVICE,
    excel_schema.ResourceType.DEFAULT_ALARMS_SETTING,
    excel_schema.ResourceType.ALARMS_SETTING,
    excel_schema.ResourceType.SENSOR_READING_TO_BACNET,
    excel_schema.ResourceType.GENERIC_DEVICE,
    excel_schema.ResourceType.SENSOR_CALIBRATION,
]


def read_excel(filepath: str) -> Dict[excel_schema.ResourceType, pd.DataFrame]:
    ret = {}
    for resource_type in RESOURCE_IN_EXCEL:
        dataframe = pd.read_excel(
            filepath,
            sheet_name=resource_type.value,
            dtype={"DeviceAddress": str, "uplinkInterval": str},
        )
        ret[resource_type] = dataframe.fillna("")
    return ret


def get_site_name(filepath: str) -> str:
    sitename = filepath.split("/")[-1].split("-")[0]
    return sitename


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "mode",
        metavar="export/import",
        type=str,
        help="To export or import information",
    )
    parser.add_argument("-c", "--config", help="Config file path.")
    args = parser.parse_args()

    try:
        with open(args.config, "r", encoding="utf-8") as yamlfile:
            config_file = yaml.load(yamlfile, Loader=yaml.FullLoader)
            config = excel_schema.Config(**config_file)
            logger.info("config read successfully.")

    except IOError:
        logger.error("Config Read Failed.")

    stores.chirpstack.conn_config.ConnectionConfig(
        host=config.chirpstack.host,
        port=config.chirpstack.port,
        username=config.chirpstack.username,
        password=config.chirpstack.password,
    )

    stores.thingsboard.conn_config.ConnectionConfig(
        host=config.thingsboard.host,
        port=config.thingsboard.port,
        username=config.thingsboard.username,
        password=config.thingsboard.password,
    )

    stores.neo4j.gdb_client.GdbClient(
        uri=config.neo4j.host + ":" + config.neo4j.port,
        username=config.neo4j.username,
        password=config.neo4j.password,
    )

    if args.mode == "import":
        resources_from_excel = read_excel(config.excel_path)
        site_name = get_site_name(config.excel_path)
        services.imports.import_resource(site_name, resources_from_excel, config)
        services.imports.import_to_graphdb(site_name, resources_from_excel)

    logger.info("Import finished.")


if __name__ == "__main__":
    main()
