from typing import Dict

import pandas as pd
import argparse
import yaml
from loguru import logger

import excel_schema
import stores.conn_config

RESOURCE_IN_EXCEL = [
    excel_schema.ResourceType.USERGROUP,
    excel_schema.ResourceType.USER,
    excel_schema.ResourceType.CLIENT,
    excel_schema.ResourceType.RESOURCE,
    excel_schema.ResourceType.SCPOES,
    excel_schema.ResourceType.PERMISSION,
]


def read_excel(filepath: str) -> dict[excel_schema.ResourceType, pd.DataFrame]:
    excel_df = {}
    for resource_type in RESOURCE_IN_EXCEL:
        dataframe = pd.read_excel(
            filepath,
            sheet_name=resource_type.value,
        )
        excel_df[resource_type] = dataframe.fillna("")
    return excel_df


def get_realm_name(filepath: str) -> str:
    realm_name = filepath.split("/")[-1].split("-")[0]
    return realm_name


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="Config file path.")
    args = parser.parse_args()

    try:
        with open(args.config, "r", encoding="utf-8") as yamlfile:
            config_file = yaml.load(yamlfile, Loader=yaml.FullLoader)
            config = excel_schema.Config(**config_file)
            logger.info("config read successfully.")
    except IOError:
        logger.error("Config Read Failed.")


if __name__ == "__main__":
    stores.conn_config.ConnectionConfig(
        host="127.0.0.1", port="8080", username="admin", password="admin"
    )

    mykeycloak = stores.conn_config.ConnectionConfig.get_instance()
    token = mykeycloak.get_token()
    logger.info(token)
