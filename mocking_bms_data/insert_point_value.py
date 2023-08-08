import json
import requests

file_path = "/Users/williamleung/Documents/fastapi_playground/mocking_bms_data/bms_mocked_data_for_lg3_opt.json"

temp_value = {"value": 0, "timestamp": "2023-06-29T08:53:37.180Z"}
get_url = "http://172.16.14.49:30971/api/v1/points?path_prefixes="

with open(file_path, "r") as f:
    data = json.load(f)

values = []
for item in data:
    standard_name = str(item["standard_name"])
    path = "/" + standard_name.replace(".", "/")
    value = temp_value.copy()
    value["value"] = item["value"]
    print(value)
    r = requests.get(get_url + path)
    if r.status_code == 200:
        print(r.json())
        id = r.json()[0]["id"]

        p = requests.post(
            f"http://172.16.14.49:30971/api/v1/points/{id}/values", json=value
        )
