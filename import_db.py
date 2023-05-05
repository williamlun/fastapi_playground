import psycopg2
import uuid
import csv
import requests


name_to_ams_device_map = {}
serial_id_to_device_id_map = {}

host = input("Enter the host name: ")
port = input("Enter the port number: ")
username = input("Enter the username: ")
password = input("Enter the password: ")
database = input("Enter the database name: ")
data_svc_secret = input("Enter the data-service client secret: ")

print("Authorizing with Asset Management Service...")

token_response = requests.post(
    f"https://{host}/asset-mgmt-service/token",
    params={
        "grant_type": "client_credentials",
        "client_id": "data-service",
        "client_secret": data_svc_secret,
    },
    verify=False,
)

if not token_response.ok:
    raise Exception(token_response.text)

token = token_response.json()["access_token"]

print("Authorization success!")

print("Reading devices from Asset Management Service...")

device_response = requests.get(
    f"https://{host}/asset-mgmt-service/api/v1/devices",
    headers={"Authorization": f"Bearer {token}"},
    verify=False,
)

if not device_response.ok:
    raise Exception(device_response.text)

for device in device_response.json():
    name_to_ams_device_map[device["name"]] = device

print("Done loading devices from Asset Management Service!")
print(name_to_ams_device_map)

print("Connecting to database...")

conn = psycopg2.connect(
    f"dbname={database} user={username} password={password} host={host} port={port}"
)
conn.autocommit = True

cur = conn.cursor()

print("Reading devices from CSV...")

with open("device.csv", "r") as f:
    csv_reader = csv.reader(f, delimiter=",")
    for row in csv_reader:
        device_display_name = ""
        device_id = uuid.uuid5(uuid.NAMESPACE_DNS, row[1])
        if name_to_ams_device_map.get(row[1], None):
            device_display_name = name_to_ams_device_map[row[1]]["displayName"]
            device_id = uuid.UUID(name_to_ams_device_map[row[1]]["id"])
        serial_id_to_device_id_map[row[0]] = device_id.hex
        cur.execute(
            f"INSERT INTO device (id, name, display_name) VALUES ('{device_id.hex}', '{row[1]}', '{device_display_name}') ON CONFLICT DO NOTHING"
        )

print("Done reading devices from CSV!")
print(serial_id_to_device_id_map)

print("Reading telemetry data from CSV...")

with open("telemetry_data.csv", "r") as f:
    csv_reader = csv.reader(f, delimiter=",")
    for row in csv_reader:
        device_id = serial_id_to_device_id_map[row[1]]
        cur.execute(
            f"INSERT INTO telemetry_data (timestamp, device_id, key, value) VALUES ('{row[0]}', '{device_id}', '{row[2]}', {row[3]}) ON CONFLICT DO NOTHING"
        )

print("Done reading telemetry data from CSV!")

cur.close()

print("The import completed successfully!")
