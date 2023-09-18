import json
import os
import uuid
import datetime
import requests
import random


bms_data_service_url = "0.0.0.0:8003"
site_name = "ATALDEV"
site_id = "78e71a60-326f-575b-9972-fb8b4f2df2f5"
number_of_point_need_fake_data = 10  # only 1000 fake points in total

start_datetime = datetime.datetime(2023, 8, 15, 0, 0, 0)
interval = datetime.timedelta(minutes=15)
end_datetime = datetime.datetime(2023, 8, 16, 0, 0, 0)

# Open the JSON file
with open("./bms-data-service/point.json") as file:
    # Load the JSON data into a Python dictionary
    data_dict = json.load(file)

points = data_dict["sensor"]
points = [point["std_name"] for point in points]
print(points)

fake_data_points = points[0:number_of_point_need_fake_data]
print(fake_data_points)

for point in fake_data_points:
    point_uuid = uuid.uuid5(namespace=uuid.NAMESPACE_OID, name=str((site_name, point)))
    point_id = str(point_uuid)

    time = start_datetime
    while time < end_datetime:
        value = round(random.uniform(0.0, 100.0), 1)
        url = f"http://{bms_data_service_url}/api/v1/sites/{site_id}/points/{point_id}/data?timestamp={time.isoformat()}&value={value}"
        payload = {}
        headers = {"Content-Type": "application/json"}
        response = requests.request("POST", url, headers=headers, data=payload)
        time += interval
        print(time)
