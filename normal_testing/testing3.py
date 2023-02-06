import requests


def main():
    login_url = "http://172.16.12.207:30909/api/auth/login"
    data = {"username": "tenant@thingsboard.org", "password": "tenant"}
    header = {"content-type": "application/json"}
    jwt_response = requests.post(
        login_url, headers=header, json=data, timeout=10
    ).json()
    token = jwt_response["token"]

    _req_header = {
        "accept": "application/json",
        "X-Authorization": f"Bearer {token}",
    }

    payload = {
        "method": "down",
        "params": {
            "confirmed": True,
            "fPort": 7,
            "data": "krAHAAAAAAAAAAA=",
            "applicationName": "Netvox-R831D",
            "devEUI": "7012018a559519f3",
        },
        "timeout": 300000,
    }
    response = requests.post(
        f"http://172.16.12.207:30909/api/plugins/rpc/twoway/c035c020-954a-11ed-896d-1d30edc3ff31",
        json=payload,
        headers=_req_header,
        timeout=300,
    )
    if response.status_code >= 300:
        print("on9")

    print(response.text)


if __name__ == "__main__":
    main()
