import aiohttp
import asyncio
from loguru import logger
from aiohttp import TCPConnector
import requests


async def _check_permission(user_token: str, resource: str, scope: str) -> bool:
    headers = {
        "Authorization": f"Bearer {user_token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    logger.info(f"headers: {headers}")
    url = "https://172.16.12.207/auth/realms/ataldev/protocol/openid-connect/token"
    client_id = "data-service"
    grant_type = "urn:ietf:params:oauth:grant-type:uma-ticket"
    logger.info(f"url: {url}")
    payload = (
        f"audience={client_id}&"
        f"grant_type={grant_type}&"
        f"response_mode=decision&"
        f"permission={resource}#{scope}"
    )
    logger.info(f"payload: {payload}")
    async with aiohttp.ClientSession(
        connector=TCPConnector(verify_ssl=False)
    ) as session:
        async with session.post(url, headers=headers, data=payload) as r:
            response = await r.json()
            logger.info(response)
            if r.status == 403:
                return False
            return response


async def main():
    result = await _check_permission(
        user_token="eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJEOXEzdmxoVGhNODBHNE1tNC1mZ1IxX0liYU9IYTRuQlJCWHZBR2xURE5zIn0.eyJleHAiOjE2NzU0MTEyMzgsImlhdCI6MTY3NTQxMDkzOCwiYXV0aF90aW1lIjoxNjc1NDA5MjM1LCJqdGkiOiJmNGE5YWE1OS1kODY1LTQzZWQtYjVkYy03YmEyNjRjYTYyZDIiLCJpc3MiOiJodHRwczovLzE3Mi4xNi4xMi4yMDcvYXV0aC9yZWFsbXMvYXRhbGRldiIsImF1ZCI6WyJncmFmYW5hIiwiYWNjb3VudCJdLCJzdWIiOiJkMmQ1OGY5NS02NDU5LTRjZWUtOWI0Ny1hNjgwYzdkNzFiMWMiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiIzcmQtcGFydHkiLCJzZXNzaW9uX3N0YXRlIjoiZGFkZDBmZDAtNTE0NC00MmFiLWIyZTgtNjFmMmNkODRiZWE4IiwiYWNyIjoiMCIsInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJvZmZsaW5lX2FjY2VzcyIsInVtYV9hdXRob3JpemF0aW9uIiwiZGVmYXVsdC1yb2xlcy1hdGFsZGV2Il19LCJyZXNvdXJjZV9hY2Nlc3MiOnsiZ3JhZmFuYSI6eyJyb2xlcyI6WyJhZG1pbiJdfSwiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJwcm9maWxlIGVtYWlsIiwic2lkIjoiZGFkZDBmZDAtNTE0NC00MmFiLWIyZTgtNjFmMmNkODRiZWE4IiwiZW1haWxfdmVyaWZpZWQiOnRydWUsInByZWZlcnJlZF91c2VybmFtZSI6ImF0YWwiLCJnaXZlbl9uYW1lIjoiIiwiZmFtaWx5X25hbWUiOiIiLCJlbWFpbCI6ImF0YWxAdGIuY29tIn0.cTJju4BbYSGdiagwD4rwa8Wc9nEsD7jdFFlCuoEVZhfkw0j8He6NLJkMl7ujkAZKCm-N2FxrMFhJr41Gackb_c8khn3E4Hdri6YbFl8Hqb3eGhqfjWJbnteB0AE5qxoq3Wy_ZUeeViYivPT7_QMos8_dZju08du9Drc5iYvZz8hDC1qm6e9jx7_-Z8BSHA3lL3aUOmvoddF9_Pmdz-bISZZnon9UyEe3G_xM60QyHObexc1y0YWIE1W-UrBsGHMSyA0zspltvsO81MoEN2m9908uJUP9_VW7rzfqtj9wwpmflRWHvSyvqae_Any0FiYdQQLJnQylEinUNVzvuP0HTA",
        resource="site_a/*",
        scope="data:realtime:read",
    )
    print(result)


if __name__ == __name__:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
