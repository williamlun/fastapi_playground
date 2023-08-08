import requests
import datetime

temp_value = {"value": 7.3, "timestamp": datetime.datetime.now().isoformat()}
id = "343e2b7b-3177-5498-b617-edb57865e781"
print(temp_value)
p = requests.post(
    f"http://172.16.14.49:30971/api/v1/points/{id}/values", json=temp_value
)

print(p.text)
