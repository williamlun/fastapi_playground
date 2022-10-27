"""stoore for keycloak"""
import requests
from loguru import logger
from keycloak import KeycloakOpenID, KeycloakAdmin
from fastapi import HTTPException, status

_url = "http://127.0.0.1:8080"
_realms = "atal"
_client_id = "demo_service"
_client_secret = "91djjv6bCPQhDa8WndrnyQdIsB0pF3Cd"

keycloak_openid = KeycloakOpenID(
    server_url=_url,
    client_id=_client_id,
    realm_name=_realms,
    client_secret_key=_client_secret,
)


def manual_login(username, password):
    body = {
        "client_id": _client_id,
        "username": username,
        "password": password,
        "grant_type": "password",
        "client_secret": _client_secret,
    }

    response = requests.post(
        f"{_url}/realms/{_realms}/protocol/openid-connect/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=body,
    )

    return response.json()


def lib_login(username, password):
    token = keycloak_openid.token(username, password)
    return token


def get_access_code(redirect_uri):
    access_code = keycloak_openid.auth_url(redirect_uri=redirect_uri)
    return access_code


def get_token_from_code(code, redirect_uri):
    logger.info(redirect_uri)
    token = keycloak_openid.token(
        grant_type=["authorization_code"], code=code, redirect_uri=redirect_uri
    )
    return token


def logout(token):
    keycloak_openid.logout(token["refresh_token"])
    return "successfully logged out"


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
