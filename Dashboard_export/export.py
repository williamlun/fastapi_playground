"""import script"""
import requests
import os
import json
import zipfile
from loguru import logger

THINGBOARD_HOST = os.getenv("THINGBOARD_HOST", "172.16.14.50")
THINGBOARD_USERNAME = os.getenv("THINGBOARD_USERNAME", "tenant@thingsboard.org")
THINGSBOARD_PASSWORD = os.getenv("THINGSBOARD_PASSWORD", "tenant")
FILE_NAME = os.getenv("FILE_NAME", "dashboard_export.zip")
token = ""

default_dashboard = [
    "Thermostats",
    "Firmware",
    "Rule Engine Statistics",
    "Software",
    "Gateways",
]


#################################Connection############################################
def get_url(resource: str) -> str:
    return f"https://{THINGBOARD_HOST}/api/{resource}"


def get_token():
    login_url = get_url("auth/login")
    req_body = {"username": THINGBOARD_USERNAME, "password": THINGSBOARD_PASSWORD}
    jwt_response = requests.post(
        login_url, json=req_body, timeout=10, verify=False
    ).json()
    return jwt_response["token"]


###########################################################################################


######################################### Dashboard ###################################
def get_all_dashboard() -> list:
    dashboard_url = get_url("tenant/dashboards")
    response = requests.get(
        dashboard_url,
        headers={"Authorization": f"Bearer {token}"},
        params={"pageSize": 2147483647, "page": 0},
        timeout=10,
        verify=False,
    )
    return response.json()


def filter_dashboard(dashboards: list) -> list:
    dashboard_needed = [
        dashboard
        for dashboard in dashboards
        if dashboard["title"] not in default_dashboard
    ]
    return dashboard_needed


def extract_dashboard_id(dashboard_needed: list):
    dashboard_ids = [dashboard["id"]["id"] for dashboard in dashboard_needed]
    return dashboard_ids


def get_dashboard_json(id_: str) -> dict:
    dashboard_url = get_url(f"dashboard/{id_}")
    response = requests.get(
        dashboard_url,
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
        verify=False,
    )
    return response.json()


#########################################################################################


##################################Thingsboard Stores get name by id##########################################
def get_device_name_by_id(id_: str):
    device_url = get_url(f"device/info/{id_}")
    response = requests.get(
        device_url,
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
        verify=False,
    )
    return response.json()["name"]


def get_asset_name_by_id(id_: str):
    asset_url = get_url(f"asset/info/{id_}")
    response = requests.get(
        asset_url,
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
        verify=False,
    )
    return response.json()["name"]


def get_tenant_name_by_id(id_: str):
    tenant_url = get_url(f"tenant/{id_}")
    response = requests.get(
        tenant_url,
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
        verify=False,
    )
    return response.json()["name"]


def get_customer_name_by_id(id_: str):
    customer_url = get_url(f"customer/{id_}")
    response = requests.get(
        customer_url,
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
        verify=False,
    )
    return response.json()["name"]


def get_user_name_by_id(id_: str):
    user_url = get_url(f"user/{id_}")
    response = requests.get(
        user_url,
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
        verify=False,
    )
    return response.json()["name"]


def get_dashboard_name_by_id(id_: str):
    dashboard_url = get_url(f"dashboard/{id_}")
    response = requests.get(
        dashboard_url,
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
        verify=False,
    )
    return response.json()["title"]


############################################################################################


###################################Entity handler###########################################


def _get_entity_name_function(entity_type: str):
    entity_type_mapping = {
        "DEVICE": get_device_name_by_id,
        "ASSET": get_asset_name_by_id,
        "TENANT": get_tenant_name_by_id,
        "CUSTOMER": get_customer_name_by_id,
        "USER": get_user_name_by_id,
        "DASHBOARD": get_dashboard_name_by_id,
        "CURRENT_CUSTOMER": get_customer_name_by_id,
        "CURRENT_USER": get_user_name_by_id,
    }
    return entity_type_mapping[entity_type]


def _entity_handler(entity_type: str, entity_id: str):
    name = _get_entity_name_function(entity_type)(entity_id)
    content = {"entity_id": entity_id, "entity_type": entity_type, "name": name}
    return content


def signle_entity_handler(signle_entity: dict):
    entity_type = signle_entity["entityType"]
    entity_id = signle_entity["id"]
    handle_list = [
        "DEVICE",
        "ASSET",
        "TENANT",
        "CUSTOMER",
        "USER",
        "DASHBOARD",
        "CURRENT_CUSTOMER",
        "CURRENT_USER",
    ]
    if entity_type in handle_list:
        try:
            return {entity_id: _entity_handler(entity_type, entity_id)}
        except:
            return {}
    return {}


def entitylist_handler(entity_type: str, entity_ids: list):
    mappings = {}
    for entity_id in entity_ids:
        mappings.update(
            signle_entity_handler({"entityType": entity_type, "id": entity_id})
        )
    return mappings


###########################################################################################


def create_aliases_mapping(alias: dict):
    if alias["filter"]["type"] == "singleEntity":
        mapping = signle_entity_handler(alias["filter"]["singleEntity"])
        return mapping

    if alias["filter"]["type"] == "entityList":
        mapping = entitylist_handler(
            alias["filter"]["entityType"], alias["filter"]["entityList"]
        )
        return mapping
    return {}


def process_dashboard(id_):
    dashboard_json = get_dashboard_json(id_)
    try:
        entity_aliases = dashboard_json["configuration"]["entityAliases"]
        mappings = {}
        for alias in entity_aliases.values():
            mappings.update(create_aliases_mapping(alias))
    except:
        mappings = {}
    dashboard_json["mapping"] = mappings
    dashboard_json.pop("id")
    dashboard_json.pop("createdTime")
    dashboard_json.pop("tenantId")
    return dashboard_json


def export():
    logger.info("Start export dashboard")
    global token
    token = get_token()

    all_dashboard = get_all_dashboard()["data"]
    dashboard_needed = filter_dashboard(all_dashboard)
    dashboard_ids = extract_dashboard_id(dashboard_needed)

    with zipfile.ZipFile(f"/dashboard/{FILE_NAME}", "w") as zip_file:
        for id_ in dashboard_ids:
            result = process_dashboard(id_)
            dashboard_name = result["title"]
            data = json.dumps(result, indent=4)
            zip_file.writestr(f"{dashboard_name}.json", data)
    logger.info("Finish export dashboard")
