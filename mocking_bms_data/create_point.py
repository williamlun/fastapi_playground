import json
import requests

file_path = "/Users/williamleung/Documents/fastapi_playground/mocking_bms_data/bms_mocked_data_for_lg3_opt.json"

temp_point = {
    "path": "/ATAL/twosky/18F/william/test/demo/24",
    "data_type": "datetime",
    "unit": "",
    "status": "good",
    "is_writable": True,
    "is_forcible": True,
}

with open(file_path, "r") as f:
    data = json.load(f)

points = []
for item in data:
    standard_name = str(item["standard_name"])
    path = "/" + standard_name.replace(".", "/")
    point = temp_point.copy()
    point["path"] = path
    if item["value"] == True or item["value"] == False:
        point["data_type"] = "boolean"
    else:
        point["data_type"] = "float"
    points.append(point)
    print(point)


url = "http://172.16.14.49:30971/api/v1/points"


for point in points:
    payload = json.dumps(point)
    headers = {"Content-Type": "application/json"}
    r = requests.post(url, headers=headers, data=payload)
    print(r.text)
