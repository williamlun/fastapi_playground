import requests


def get_url(resource: str) -> str:
    return f"https://172.16.14.142:14322/api/{resource}"


def get_token() -> str:
    login_url = get_url("auth/login")
    req_body = {"username": "tenant@thingsboard.org", "password": "Mh8kBUn7DSznU9"}
    jwt_response = requests.post(
        login_url, json=req_body, timeout=10, verify=False
    ).json()
    return jwt_response["token"]


def get_headers(token: str) -> dict:
    return {
        "accept": "application/json",
        "X-Authorization": f"Bearer {token}",
    }


def get_bacnet_device(header):
    svc_url = get_url("tenant/devices")
    response = requests.get(
        f"{svc_url}",
        params={"pageSize": 2147483647, "page": 0, "textSearch": "bacnet"},
        headers=header,
        timeout=10,
        verify=False,
    )
    devices = response.json()["data"]
    if len(devices) == 0:
        return None
    return devices[0]


def get_related_devices_id(header, bacnet_device_id) -> list[str]:
    svc_url = get_url("relations/info")
    response = requests.get(
        f"{svc_url}",
        params={"toId": bacnet_device_id, "toType": "DEVICE"},
        headers=header,
        timeout=10,
        verify=False,
    )
    return [device["from"]["id"] for device in response.json()]


if __name__ == "__main__":
    header = get_headers(get_token())
    result = get_bacnet_device(header)
    print(header)
