import aiohttp
import asyncio
from loguru import logger
import requests
import random
import time
thingsboard_url = "https://172.16.14.49/"

devices_access_token = [
    # "cftGM9eYhEEVfao9Qrnf",
    # "eesOVkXgwFNc7gqVa61Z",
    # "MIe3DAcitoXXDLJuc1OC",
    # "Gav4AOkUZvkeB47gg0cA",
    # "btFPbYtg6OUWbpwQU1Pd",
    # "IvVMhwD3eTKG7iGSGnjE",
    # "K8lStKLccNSYCIAGMNHv",
    # "mDaTl05Z6Ufv1ggnW0PR",
    # "f96XVw0aVrLhWOxHfGLc"
    "mgGxBRZCjFLamvb2BWHQ"
]

while True:
    payload = { 
        # "temperature": random.uniform(0, 50), 
        # "humidity": random.randint(0, 100),
        # "rssi": random.uniform(0, 3),
        # "loRaSNR": random.uniform(0, 10),
        # "batteryLevel": random.randint(0, 100),
        # "co2": random.randint(0, 100),
        # "tvoc": random.randint(0, 100),
        # "ch4": random.randint(0, 100),
        # "co": random.randint(0, 100),
        "kFactor" :random.randint(0, 100),
    }
    for access_token in devices_access_token:
        url = thingsboard_url + "api/v1/" + access_token + "/telemetry"
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, json=payload, verify=False)
    time.sleep(1)
