import requests
import os
import json
import zipfile

THINGBOARD_HOST = os.getenv("THINGBOARD_HOST", "172.16.14.49")
THINGBOARD_USERNAME = os.getenv("THINGBOARD_USERNAME", "tenant@thingsboard.org")
THINGSBOARD_PASSWORD = os.getenv("THINGSBOARD_PASSWORD", "admin123ex")
FILE_NAME = "dashboard_export.zip"
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


def process_dashboard(dashboard: dict):
    # extract mapping
    mapping = dashboard.pop("mapping")
    # process mapping to UUID:UUID
    uuid_mapping = {}

    # find and replace id in dashboard
    # post dashboard


######################################################################################


def main():
    global token
    token = get_token()

    dashboards = extract_dashboard_from_zip(FILE_NAME)
    for dashboard in dashboards:
        new_dashboard = process_dashboard(dashboard)

    print(all_dashboard)


if __name__ == "__main__":
    main()
