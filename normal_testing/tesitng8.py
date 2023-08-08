import io
import requests
import json
import itertools
from requests.auth import HTTPBasicAuth
import enum
from loguru import logger

# url = "http://172.16.14.228:8000/mqtt-config"
# username = "username"
# password = "password"
# auth = HTTPBasicAuth(username, password)
# data = {"asdfjklasdfjk": "asdffasd", "username": "username", "password": "password"}


# data_as_file = {"file": io.BytesIO(json.dumps(data).encode())}


# response = requests.post(url=url, auth=auth, files=data_as_file)


# print(response.json())

# list1 = [1, 2, 3, 4, 5]
# list2 = [4, 5, 6, 7, 8]

# list1 = [i for i in list1 if i not in list2]
# print("List1 after removal:", list1)
# print("List2 after removal:", list2)


# logger.info(
#     "Received uplink message from device [{}], with payload {}",
#     "123",
#     "456",
# )

nested_list = [[1, 5, 6, 2], [3, 4, 5, 5, 6], [3, 7, 8, 9, 1]]

flattened_list = list(set(itertools.chain(*nested_list)))

print(flattened_list)
