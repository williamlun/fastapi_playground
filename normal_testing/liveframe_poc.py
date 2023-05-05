import requests
import asyncio
import aiohttp
import json

login_url = "http://172.16.14.50:31808/api/internal/login"
username = "admin"
password = "78prtjzDvHMPwp"

req_body = {
    "email": username,
    "password": password,
    "username": username,
}

data_url = (
    "http://172.16.14.50:31808/#/organizations/2/gateways/ac1f09fffe0702aa/frames"
)


async def login():
    async with aiohttp.ClientSession() as session:
        async with session.post(login_url, json=req_body) as resp:
            result = await resp.json()
            print(result["jwt"])
    return result["jwt"]


async def login2():
    async with aiohttp.ClientSession() as session:
        async with session.post(login_url, json=req_body) as resp:
            result = await resp.json()
            print(result["jwt"])
    return result["jwt"]


async def get_data(headers):
    async with aiohttp.ClientSession() as session:
        async with session.get(data_url, headers=headers) as resp:
            async for line in resp.content:
                print(json.loads(line))


def normal(headers):
    s = requests.Session()
    with s.get(data_url, headers=headers, stream=True) as resp:
        for line in resp.iter_lines():
            if line:
                print(json.loads(line))


async def main():
    token = await login()
    headers = {
        "Accept": "application/json",
        "Grpc-Metadata-Authorization": f"Bearer {token}",
    }
    await get_data(headers)
    # normal(headers)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
