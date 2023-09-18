import json
import uuid
import datetime
import requests

bms_data_service_url = "0.0.0.0:8003"
site_name = "ATALDEV"
site_id = "78e71a60-326f-575b-9972-fb8b4f2df2f5"


with open("./bms-data-service/point.json") as file:
    # Load the JSON data into a Python dictionary
    data_dict = json.load(file)

points = data_dict["sensor"]
points = [point["std_name"] for point in points]
print(points)

for point in points:
    demo_dict = {
        "id": str(
            uuid.uuid5(namespace=uuid.NAMESPACE_OID, name=str((site_name, point)))
        ),
        "std_name": point,
        "data_type": "float",
        "unit": "",
        "is_virtual": True,
    }

    url = f"http://{bms_data_service_url}/api/v1/sites/{site_id}/points"
    payload = json.dumps(demo_dict)
    headers = {"Content-Type": "application/json"}
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
