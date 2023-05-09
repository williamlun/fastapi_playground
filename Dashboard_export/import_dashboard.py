import requests
import os
import json
import zipfile
from loguru import logger

THINGBOARD_HOST = os.getenv("THINGBOARD_HOST", "172.16.14.49")
THINGBOARD_USERNAME = os.getenv("THINGBOARD_USERNAME", "tenant@thingsboard.org")
THINGSBOARD_PASSWORD = os.getenv("THINGSBOARD_PASSWORD", "admin123ex")
THINGBOARD_SYSADMIN_USERNAME = os.getenv(
    "THINGBOARD_SYSADMIN_USERNAME", "sysadmin@thingsboard.org"
)
THINGSBOARD_SYSADMIN_PASSWORD = os.getenv("THINGSBOARD_SYSADMIN_PASSWORD", "admin123ex")
FILE_NAME = os.getenv("FILE_NAME", "dashboard_export.zip")
token = ""


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


def get_admin_token():
    login_url = get_url("auth/login")
    req_body = {
        "username": THINGBOARD_SYSADMIN_USERNAME,
        "password": THINGSBOARD_SYSADMIN_PASSWORD,
    }
    jwt_response = requests.post(
        login_url, json=req_body, timeout=10, verify=False
    ).json()
    return jwt_response["token"]


###########################################################################################

##################################Thingsboard Stores get id by name##########################################


def get_device_id_by_name(name: str):
    device_url = get_url("tenant/devices")
    response = requests.get(
        device_url,
        headers={"Authorization": f"Bearer {token}"},
        params={"deviceName": name},
        timeout=10,
        verify=False,
    )
    if response.status_code > 300:
        logger.info("Device with name {} not found".format(name))
        raise Exception(f"Device with name {name} not found")
    return response.json()["id"]["id"]


def get_asset_id_by_name(name: str):
    asset_url = get_url("tenant/assets")
    response = requests.get(
        asset_url,
        headers={"Authorization": f"Bearer {token}"},
        params={"assetName": name},
        timeout=10,
        verify=False,
    )
    if response.status_code > 300:
        logger.info("Device with name {} not found".format(name))
        raise Exception(f"Device with name {name} not found")
    return response.json()["id"]["id"]


def get_tenant_id_by_name(name: str):
    tenant_url = get_url("tenants")
    admin_token = get_admin_token()
    response = requests.get(
        tenant_url,
        headers={"Authorization": f"Bearer {admin_token}"},
        params={"pageSize": 2147483647, "page": 0, "textSearch": name},
        timeout=10,
        verify=False,
    )
    results = response.json()["data"]
    for result in results:
        if result["name"] == name:
            return result["id"]["id"]
    raise Exception(f"Tenant {name} not found")


def get_customer_id_by_name(name: str):
    customer_url = get_url("customers")
    response = requests.get(
        customer_url,
        headers={"Authorization": f"Bearer {token}"},
        params={"pageSize": 2147483647, "page": 0, "textSearch": name},
        timeout=10,
        verify=False,
    )
    results = response.json()["data"]
    for result in results:
        if result["name"] == name:
            return result["id"]["id"]
    raise Exception(f"Customer {name} not found")


def get_user_id_by_name(name: str):
    user_url = get_url("users")
    response = requests.get(
        user_url,
        headers={"Authorization": f"Bearer {token}"},
        params={"pageSize": 2147483647, "page": 0, "textSearch": name},
        timeout=10,
        verify=False,
    )
    results = response.json()["data"]
    for result in results:
        if result["name"] == name:
            return result["id"]["id"]
    raise Exception(f"User {name} not found")


def get_dashboard_id_by_name(name: str):
    dashboard_url = get_url("tenant/dashboards")
    response = requests.get(
        dashboard_url,
        headers={"Authorization": f"Bearer {token}"},
        params={"pageSize": 2147483647, "page": 0, "textSearch": name},
        timeout=10,
        verify=False,
    )
    results = response.json()["data"]
    for result in results:
        if result["name"] == name:
            return result["id"]["id"]
    raise Exception(f"Dashboard {name} not found")


###########################################################################################


###################################Entity handler###########################################


def _get_entity_name_function(entity_type: str):
    entity_type_mapping = {
        "DEVICE": get_device_id_by_name,
        "ASSET": get_asset_id_by_name,
        "TENANT": get_tenant_id_by_name,
        "CUSTOMER": get_customer_id_by_name,
        "USER": get_user_id_by_name,
        "DASHBOARD": get_dashboard_id_by_name,
        "CURRENT_CUSTOMER": get_customer_id_by_name,
        "CURRENT_USER": get_user_id_by_name,
    }
    return entity_type_mapping[entity_type]


def _entity_handler(entity: dict):
    entity_type = entity["entity_type"]
    entity_name = entity["name"]
    entity
    try:
        result_id = _get_entity_name_function(entity_type)(entity_name)
    except BaseException:
        logger.error(f"Entity {entity_type}: {entity_name} not found")
        result_id = entity["entity_id"]

    return result_id


###########################################################################################


####################################Dashboard#########################################
def extract_dashboard_from_zip(file_name: str):
    dashboards = []
    with zipfile.ZipFile(file_name, "r") as archive:
        for file_name in archive.namelist():
            with archive.open(file_name) as file:
                dashboard_data = json.load(file)
                dashboards.append(dashboard_data)
    return dashboards


def update_dashboard(dashboard: dict, mapping: dict):
    for old_uuid, new_uuid in mapping.items():
        dashboard = recursive_replace(dashboard, old_uuid, new_uuid)
    return dashboard


def recursive_replace(obj, old_string, new_string):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, (dict, list)):
                recursive_replace(value, old_string, new_string)
            elif isinstance(value, str):
                obj[key] = value.replace(old_string, new_string)
    elif isinstance(obj, list):
        for i in range(len(obj)):
            if isinstance(obj[i], (dict, list)):
                recursive_replace(obj[i], old_string, new_string)
            elif isinstance(obj[i], str):
                obj[i] = obj[i].replace(old_string, new_string)
    return obj


def post_dashboard(dashboard: dict):
    pass
    dashboard_url = get_url("dashboard")
    response = requests.post(
        dashboard_url,
        headers={"Authorization": f"Bearer {token}"},
        json=dashboard,
        timeout=10,
        verify=False,
    )
    if response.status_code > 300:
        logger.error(f"Dashboard {dashboard['name']} not posted")
        raise Exception(f"Dashboard {dashboard['name']} not posted")
    return response.json()


def save_dashboard(data: dict):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def process_dashboard(dashboard: dict):
    # extract mapping
    mapping = dashboard.pop("mapping")
    # process mapping to UUID:UUID
    uuid_mapping = {}
    for key, value in mapping.items():
        result_uuid = _entity_handler(value)
        uuid_mapping.update({key: result_uuid})
    # find and replace id in dashboard
    result_dashboard = update_dashboard(dashboard, uuid_mapping)
    # post dashboard
    post_result = post_dashboard(result_dashboard)

    return result_dashboard


######################################################################################


def import_dashboard():
    logger.info("Start import dashboard")
    global token
    token = get_token()

    dashboards = extract_dashboard_from_zip(f"/dashboard/{FILE_NAME}")
    for dashboard in dashboards:
        new_dashboard = process_dashboard(dashboard)
    logger.info("Finish import dashboard")
