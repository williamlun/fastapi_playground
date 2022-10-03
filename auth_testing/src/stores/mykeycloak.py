"""stoore for keycloak"""
import requests
from loguru import logger
from keycloak import KeycloakOpenID, KeycloakAdmin
from fastapi import HTTPException, status

_url = "http://127.0.0.1:30769"
_realms = "atal"
_client_id = "fastapi_play"
_client_secret = "Xmyejkc5ngfLo8t23WnXOl7bB6bgUqJa"

keycloak_openid = KeycloakOpenID(
    server_url=_url,
    client_id=_client_id,
    realm_name=_realms,
    # client_secret_key="x8ntdcHCJTYVbjpe7XgBd34962nqRvxd",
)

keycloak_admin = KeycloakAdmin(
    server_url=_url,
    username="admin",
    password="admin",
    realm_name="master",
    user_realm_name="atal",
    verify=True,
)


def login(username: str, password: str):
    body = {
        "client_id": _client_id,
        "username": username,
        "password": password,
        "grant_type": "password",
        "client_secret": _client_secret,
    }
    logger.info(body)

    response = requests.post(
        f"{_url}/realms/{_realms}/protocol/openid-connect/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=body,
    )

    return response.json()


def decode_token(token):
    KEYCLOAK_PUBLIC_KEY = (
        "-----BEGIN PUBLIC KEY-----\n"
        + keycloak_openid.public_key()
        + "\n-----END PUBLIC KEY-----"
    )
    logger.info(KEYCLOAK_PUBLIC_KEY)
    options = {"verify_signature": True, "verify_aud": False, "verify_exp": True}
    try:
        token_info = keycloak_openid.decode_token(
            token, key=KEYCLOAK_PUBLIC_KEY, options=options
        )

    except HTTPException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="HTTP_401_UNAUTHORIZED"
        ) from e
    logger.info(f"token info : {token_info}")
    return token_info


def get_role():
    logger.info("start get role")
    realm_roles = keycloak_admin.get_realm_roles()
    logger.info(f"{realm_roles}")
    return realm_roles
