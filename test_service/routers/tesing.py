from multiprocessing.managers import Token
from typing import Union, Optional
import fastapi
from fastapi import status, Depends, Cookie
import requests
import json

from fastapi import HTTPException, status, Response, Request
import keycloak.exceptions
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
    OAuth2PasswordRequestForm,
    OAuth2AuthorizationCodeBearer,
)
from loguru import logger
import requests
from keycloak import KeycloakOpenID, KeycloakAdmin

BASE_URL = "http://127.0.0.1:8077"

_url = "http://127.0.0.1:8080"
_realms = "atal"
_client_id = "demo_service"
_client_secret = "Oav1GLwKZdDIBySvnMv7tGgZJjwZyqGh"

keycloak_openid = KeycloakOpenID(
    server_url=_url,
    client_id=_client_id,
    realm_name=_realms,
    client_secret_key=_client_secret,
)

keycloak_admin = KeycloakAdmin(
    server_url="http://localhost:8080",
    username="admin",
    password="admin",
    realm_name="master",
    verify=True,
)
keycloak_admin.realm_name = "atal"

# User counter
count_users = keycloak_admin.users_count()
logger.info(f"count_user: {count_users}")

# Get users Returns a list of users, filtered according to query parameters
users = keycloak_admin.get_users({})
logger.info(f"users: {users}")

user_id_keycloak = keycloak_admin.get_user_id("example@example.com")
logger.info(f"user_id_keycloak: {user_id_keycloak}")

credentials = keycloak_admin.get_credentials(user_id=user_id_keycloak)
logger.info(f"credentials: {credentials}")

clients = keycloak_admin.get_clients()
# logger.info(f"clients: {clients}")

client_id = keycloak_admin.get_client_id("demo_service")
logger.info(f"demo service client_id: {client_id}")

groups = keycloak_admin.get_groups()
logger.info(f"groups: {groups}")

group = keycloak_admin.get_group_by_path(path="/site_b/user", search_in_subgroups=True)
logger.info(f"group id: {group['id']}")

##testing create user
# payload = {
#     "email": "example@example.com",
#     "username": "example@example.com",
#     "enabled": True,
#     "firstName": "Example",
#     "lastName": "Example",
#     "credentials": [
#         {
#             "value": "secret",
#             "type": "password",
#         }
#     ],
# }
# keycloak_admin.create_user(payload)


# keycloak_admin.group_user_add(user_id_keycloak, group["id"])


group = keycloak_admin.create_group({"name": "Example Group"})
