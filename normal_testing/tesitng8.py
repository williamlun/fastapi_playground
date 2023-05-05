import io
import requests
import json
from requests.auth import HTTPBasicAuth
import enum

a = int("10")
b = int(float("10.0"))

print(b)
# url = "http://172.16.14.228:8000/mqtt-config"
# username = "username"
# password = "password"
# auth = HTTPBasicAuth(username, password)
# data = {"asdfjklasdfjk": "asdffasd", "username": "username", "password": "password"}


# data_as_file = {"file": io.BytesIO(json.dumps(data).encode())}


# response = requests.post(url=url, auth=auth, files=data_as_file)


# print(response.json())

list1 = [1, 2, 3, 4, 5]
list2 = [4, 5, 6, 7, 8]

list1 = [i for i in list1 if i not in list2]
print("List1 after removal:", list1)
print("List2 after removal:", list2)
